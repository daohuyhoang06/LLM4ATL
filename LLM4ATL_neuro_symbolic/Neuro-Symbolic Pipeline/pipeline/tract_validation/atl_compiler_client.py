"""Python client for the shared Java ATL compiler CLI.

This module deliberately validates only compilation readiness. Execution and
tract checking will be added as separate clients in the same package.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_EXEC_PLUGIN_GOAL = "org.codehaus.mojo:exec-maven-plugin:3.5.0:java"
_CLI_CLASS = "org.example.AtlCompilerCli"


@dataclass(frozen=True)
class AtlCompilerDiagnostic:
    """One compile-time diagnostic emitted by the ATL compiler."""

    severity: str | None
    location: str | None
    description: str | None
    source_line: str | None = None
    column_marker: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "severity": self.severity,
            "location": self.location,
            "description": self.description,
            "source_line": self.source_line,
            "column_marker": self.column_marker,
        }


@dataclass(frozen=True)
class AtlCompileResult:
    """Normalized result returned by the Java ATL compiler CLI."""

    status: str
    atl_path: Path | None
    asm_path: Path | None
    asm_size_bytes: int
    message: str
    exception_type: str | None
    return_code: int
    diagnostics: tuple[AtlCompilerDiagnostic, ...] = ()
    stdout: str = ""
    stderr: str = ""

    @property
    def is_success(self) -> bool:
        return self.status == "COMPILED"

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "atl_path": str(self.atl_path) if self.atl_path else None,
            "asm_path": str(self.asm_path) if self.asm_path else None,
            "asm_size_bytes": self.asm_size_bytes,
            "message": self.message,
            "exception_type": self.exception_type,
            "diagnostics": [diagnostic.as_dict() for diagnostic in self.diagnostics],
            "return_code": self.return_code,
        }


class AtlCompilerClient:
    """Calls ``AtlCompilerCli`` through Maven without modifying JUnit tests."""

    def __init__(
        self,
        atl_tests_dir: Path | str | None = None,
        *,
        maven_executable: str | None = None,
        timeout_seconds: int = 120,
    ) -> None:
        self.atl_tests_dir = (
            Path(atl_tests_dir).expanduser().resolve()
            if atl_tests_dir is not None
            else self._default_atl_tests_dir()
        )
        self.maven_executable = maven_executable or ("mvn.cmd" if os.name == "nt" else "mvn")
        self.timeout_seconds = timeout_seconds

    def compile(
        self,
        atl_path: Path | str,
        asm_path: Path | str | None = None,
    ) -> AtlCompileResult:
        """Compile an ATL module and return a structured, non-throwing result."""
        input_path = Path(atl_path).expanduser().resolve()
        output_path = (
            Path(asm_path).expanduser().resolve()
            if asm_path is not None
            else self._default_asm_path(input_path)
        )

        if not self.atl_tests_dir.is_dir():
            return self._infrastructure_error(
                input_path,
                output_path,
                f"ATL_Tests directory not found: {self.atl_tests_dir}",
            )

        if not input_path.is_file():
            return AtlCompileResult(
                status="INPUT_ERROR",
                atl_path=input_path,
                asm_path=output_path,
                asm_size_bytes=0,
                message=f"ATL file not found: {input_path}",
                exception_type=None,
                return_code=2,
            )

        command = [
            self.maven_executable,
            "-q",
            "compile",
            _EXEC_PLUGIN_GOAL,
            f"-Dexec.mainClass={_CLI_CLASS}",
        ]
        environment = os.environ.copy()
        environment["ATL_COMPILER_INPUT"] = str(input_path)
        environment["ATL_COMPILER_OUTPUT"] = str(output_path)

        try:
            completed = subprocess.run(
                command,
                cwd=self.atl_tests_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=self.timeout_seconds,
                shell=False,
                env=environment,
            )
        except FileNotFoundError:
            return self._infrastructure_error(
                input_path,
                output_path,
                f"Maven executable not found: {self.maven_executable}",
            )
        except subprocess.TimeoutExpired as error:
            return self._infrastructure_error(
                input_path,
                output_path,
                f"ATL compiler timed out after {self.timeout_seconds} seconds.",
                stdout=error.stdout or "",
                stderr=error.stderr or "",
            )

        payload = self._find_compiler_payload(completed.stdout, completed.stderr)
        if payload is None:
            detail = self._last_output_line(completed.stderr) or self._last_output_line(completed.stdout)
            message = "ATL compiler CLI did not return a JSON result."
            if detail:
                message += f" Last output: {detail}"
            return self._infrastructure_error(
                input_path,
                output_path,
                message,
                return_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )

        return AtlCompileResult(
            status=str(payload.get("status", "INFRASTRUCTURE_ERROR")),
            atl_path=self._path_or_none(payload.get("atl_path")),
            asm_path=self._path_or_none(payload.get("asm_path")),
            asm_size_bytes=int(payload.get("asm_size_bytes", 0)),
            message=str(payload.get("message", "")),
            exception_type=self._string_or_none(payload.get("exception_type")),
            return_code=completed.returncode,
            diagnostics=self._diagnostics_from_payload(payload.get("diagnostics"), input_path),
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    @staticmethod
    def _default_atl_tests_dir() -> Path:
        pipeline_dir = Path(__file__).resolve().parents[1]
        return pipeline_dir.parent.parent / "ATL_Tests"

    def _default_asm_path(self, atl_path: Path) -> Path:
        return self.atl_tests_dir / "target" / "tract-validation" / "asm" / f"{atl_path.stem}.asm"

    @staticmethod
    def _find_compiler_payload(stdout: str, stderr: str) -> dict[str, Any] | None:
        for line in reversed((stdout + "\n" + stderr).splitlines()):
            candidate = line.strip()
            if not candidate.startswith("{"):
                continue
            try:
                payload = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and "status" in payload:
                return payload
        return None

    @staticmethod
    def _last_output_line(output: str) -> str:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        return lines[-1] if lines else ""

    @staticmethod
    def _path_or_none(value: Any) -> Path | None:
        return Path(value) if isinstance(value, str) and value else None

    @staticmethod
    def _string_or_none(value: Any) -> str | None:
        return value if isinstance(value, str) else None

    @classmethod
    def _diagnostics_from_payload(
        cls,
        value: Any,
        atl_path: Path,
    ) -> tuple[AtlCompilerDiagnostic, ...]:
        if not isinstance(value, list):
            return ()

        source_lines = cls._read_source_lines(atl_path)
        diagnostics: list[AtlCompilerDiagnostic] = []
        for item in value:
            if not isinstance(item, dict):
                continue

            location = cls._string_or_none(item.get("location"))
            line_number, column_number = cls._parse_location(location)
            source_line = cls._source_line(source_lines, line_number)
            column_marker = cls._column_marker(source_line, column_number)
            diagnostics.append(
                AtlCompilerDiagnostic(
                    severity=cls._string_or_none(item.get("severity")),
                    location=location,
                    description=cls._string_or_none(item.get("description")),
                    source_line=source_line,
                    column_marker=column_marker,
                )
            )
        return tuple(diagnostics)

    @staticmethod
    def _read_source_lines(atl_path: Path) -> list[str]:
        try:
            return atl_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            return []

    @staticmethod
    def _parse_location(location: str | None) -> tuple[int | None, int | None]:
        if not location:
            return None, None
        match = re.match(r"\s*(\d+):(\d+)", location)
        if match is None:
            return None, None
        return int(match.group(1)), int(match.group(2))

    @staticmethod
    def _source_line(source_lines: list[str], line_number: int | None) -> str | None:
        if line_number is None or not 1 <= line_number <= len(source_lines):
            return None
        return source_lines[line_number - 1]

    @staticmethod
    def _column_marker(source_line: str | None, column_number: int | None) -> str | None:
        if source_line is None or column_number is None:
            return None
        return " " * max(column_number - 1, 0) + "^"

    @staticmethod
    def _infrastructure_error(
        atl_path: Path,
        asm_path: Path,
        message: str,
        *,
        return_code: int = 1,
        stdout: str = "",
        stderr: str = "",
    ) -> AtlCompileResult:
        return AtlCompileResult(
            status="INFRASTRUCTURE_ERROR",
            atl_path=atl_path,
            asm_path=asm_path,
            asm_size_bytes=0,
            message=message,
            exception_type=None,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile an ATL module through the shared ATL compiler CLI.")
    parser.add_argument("atl_file", type=Path, help="Path to the ATL source file.")
    parser.add_argument("--asm-output", type=Path, help="Optional destination path for the compiled ASM file.")
    parser.add_argument("--atl-tests-dir", type=Path, help="Optional path to the ATL_Tests Maven project.")
    parser.add_argument("--timeout", type=int, default=120, help="Maximum compiler invocation time in seconds.")
    args = parser.parse_args()

    client = AtlCompilerClient(atl_tests_dir=args.atl_tests_dir, timeout_seconds=args.timeout)
    result = client.compile(args.atl_file, args.asm_output)
    print(json.dumps(result.as_dict(), ensure_ascii=False))
    return 0 if result.is_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
