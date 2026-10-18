"""Run the bundled headless AgileUML DSS adapter for one pipeline case."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


_ARTEFACT_NAMES = (
    "requirements.tagged.txt",
    "req.tl",
    "forward.tl",
)

_CLASS_MAPPING = re.compile(
    r"^Each\s+(?P<source>[A-Za-z_]\w*)\s+is\s+transformed\s+into\s+"
    r"(?:an?\s+)?(?P<target>[A-Za-z_]\w*)\.$",
    re.IGNORECASE,
)
_FEATURE_MAPPING = re.compile(
    r"^The\s+(?P<source_feature>[A-Za-z_]\w*)\s+of\s+the\s+"
    r"(?P<source>[A-Za-z_]\w*)\s+(?:is|are)\s+copied\s+to\s+the\s+"
    r"(?P<target_feature>[A-Za-z_]\w*)\s+of\s+the\s+"
    r"(?P<target>[A-Za-z_]\w*)\.$",
    re.IGNORECASE,
)


def _read_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on", "enabled"}:
        return True
    if normalized in {"0", "false", "no", "off", "disabled"}:
        return False
    raise ValueError(f"{name} must be a boolean value, got {raw!r}")


def _read_positive_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from error
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")
    return value


@dataclass(frozen=True)
class AgileUmlDssConfig:
    """Stable DSS settings used by the LLM4ATL experiment pipeline."""

    enabled: bool
    module_dir: Path
    source_chain: int
    target_chain: int
    type_match: str
    review: str

    @classmethod
    def from_env(cls, project_dir: Path) -> "AgileUmlDssConfig":
        # project_dir is LLM4ATL_Project/Neuro_Symbolic_Pipeline, therefore
        # parents[1] is the repository root containing Third_Party/.
        default_module = project_dir.parents[1] / "Third_Party" / "agileuml-dss"
        module_dir = Path(os.getenv("AGILEUML_DSS_DIR", str(default_module)))
        type_match = os.getenv("DSS_TYPE_MATCH", "fuzzy").strip().lower()
        review = os.getenv("DSS_REVIEW", "none").strip().lower()
        if type_match not in {"fuzzy", "exact"}:
            raise ValueError("DSS_TYPE_MATCH must be 'fuzzy' or 'exact'")
        if review not in {"none", "accept", "reject"}:
            raise ValueError("DSS_REVIEW must be 'none', 'accept', or 'reject'")
        return cls(
            enabled=_read_bool_env("DSS_ENABLED", True),
            module_dir=module_dir.resolve(),
            source_chain=_read_positive_int_env("DSS_SOURCE_CHAIN", 1),
            target_chain=_read_positive_int_env("DSS_TARGET_CHAIN", 1),
            type_match=type_match,
            review=review,
        )


class AgileUmlDssError(RuntimeError):
    """Raised when DSS artefacts cannot be produced safely."""


def _ecore_names(path: Path) -> tuple[set[str], set[str]]:
    """Collect EClass and structural-feature names from an Ecore document."""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as error:
        raise AgileUmlDssError(f"Cannot inspect Ecore metamodel {path}: {error}") from error

    classes: set[str] = set()
    features: set[str] = set()
    for element in root.iter():
        kind = next(
            (value for key, value in element.attrib.items() if key.endswith("}type")),
            "",
        )
        name = element.attrib.get("name")
        if not name:
            continue
        if kind.endswith("EClass"):
            classes.add(name)
        elif kind.endswith("EAttribute") or kind.endswith("EReference"):
            features.add(name)
    return classes, features


def extract_dss_requirements(
    prompt: str,
    source_metamodel: Path,
    target_metamodel: Path,
) -> str:
    """Select only conservative CNL mapping sentences from one user prompt.

    The complete prompt remains unchanged for the LLM. DSS receives only
    blank-line-separated class mappings and direct feature-copy mappings whose
    identifiers exist in the supplied source and target Ecore models.
    """
    source_classes, source_features = _ecore_names(source_metamodel)
    target_classes, target_features = _ecore_names(target_metamodel)
    selected: list[str] = []

    for block in re.split(r"\r?\n\s*\r?\n", prompt.strip()):
        sentence = " ".join(block.split())
        class_match = _CLASS_MAPPING.fullmatch(sentence)
        if class_match:
            if (
                class_match.group("source") in source_classes
                and class_match.group("target") in target_classes
            ):
                selected.append(sentence)
            continue

        feature_match = _FEATURE_MAPPING.fullmatch(sentence)
        if feature_match and (
            feature_match.group("source") in source_classes
            and feature_match.group("target") in target_classes
            and feature_match.group("source_feature") in source_features
            and feature_match.group("target_feature") in target_features
        ):
            selected.append(sentence)

    if not selected:
        raise AgileUmlDssError(
            "No DSS-compatible class or feature mapping sentence was found. "
            "Use 'Each Source is transformed into a Target.' or "
            "'The sourceFeature of the Source is copied to the targetFeature "
            "of the Target.' as a separate paragraph."
        )
    return "\n\n".join(selected)


def _find_powershell() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if executable is None:
        raise AgileUmlDssError(
            "PowerShell was not found; it is required by Third_Party/agileuml-dss."
        )
    return executable


def run_agileuml_dss(
    *,
    case_name: str,
    requirements_path: Path,
    requirements_text: str | None = None,
    source_metamodel: Path,
    target_metamodel: Path,
    output_root: Path,
    config: AgileUmlDssConfig,
) -> Path | None:
    """Create DSS artefacts and return the resulting ``forward.tl`` path.

    The adapter writes to a staging directory first. Existing successful
    artefacts are replaced only after all three expected files were produced,
    so a failed Java/Stanford run cannot leave a stale partial result that is
    later injected into an LLM prompt.
    """
    if not config.enabled:
        return None

    run_script = config.module_dir / "run_raw.ps1"
    for label, path in (
        ("DSS runner", run_script),
        ("requirements", requirements_path),
        ("source metamodel", source_metamodel),
        ("target metamodel", target_metamodel),
    ):
        if not path.is_file():
            raise AgileUmlDssError(f"Missing {label}: {path}")

    case_output = output_root / case_name
    case_output.mkdir(parents=True, exist_ok=True)
    powershell = _find_powershell()

    with tempfile.TemporaryDirectory(prefix=".staging-", dir=case_output) as temp_dir:
        staging_dir = Path(temp_dir)
        dss_requirements_path = requirements_path
        if requirements_text is not None:
            dss_requirements_path = staging_dir / "requirements.input.txt"
            dss_requirements_path.write_text(requirements_text, encoding="utf-8")
        command = [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(run_script),
            "-Source",
            str(source_metamodel),
            "-Target",
            str(target_metamodel),
            "-Requirements",
            str(dss_requirements_path),
            "-OutputDir",
            str(staging_dir),
            "-SourceChain",
            str(config.source_chain),
            "-TargetChain",
            str(config.target_chain),
            "-TypeMatch",
            config.type_match,
            "-Review",
            config.review,
        ]
        completed = subprocess.run(
            command,
            cwd=config.module_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0:
            diagnostic = (completed.stderr or completed.stdout).strip()
            raise AgileUmlDssError(
                f"AgileUML DSS failed for {case_name} with exit code "
                f"{completed.returncode}:\n{diagnostic}"
            )

        missing = [
            name for name in _ARTEFACT_NAMES
            if not (staging_dir / name).is_file()
        ]
        if missing:
            raise AgileUmlDssError(
                f"AgileUML DSS did not produce: {', '.join(missing)}"
            )

        for name in _ARTEFACT_NAMES:
            shutil.copy2(staging_dir / name, case_output / name)

    return case_output / "forward.tl"
