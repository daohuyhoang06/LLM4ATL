#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = SCRIPT_DIR / "schema"
sys.path.insert(0, str(SCHEMA_DIR))


def _json_default(value: Any) -> str:
    return str(value)


def _emit(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, ensure_ascii=False, default=_json_default))
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        return _emit(
            {
                "valid": False,
                "error_type": "UsageError",
                "error": "Usage: syntax check.py <ast_json_file>",
            }
        )

    ast_path = Path(sys.argv[1])

    try:
        from pydantic import ValidationError
        from atl_ast import ATLDocument
    except Exception as exc:
        return _emit(
            {
                "valid": False,
                "file": str(ast_path),
                "error_type": exc.__class__.__name__,
                "error": f"Could not import Pydantic ATL schema: {exc}",
            }
        )

    try:
        raw = ast_path.read_text(encoding="utf-8")
    except Exception as exc:
        return _emit(
            {
                "valid": False,
                "file": str(ast_path),
                "error_type": exc.__class__.__name__,
                "error": f"Could not read AST JSON file: {exc}",
            }
        )

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _emit(
            {
                "valid": False,
                "file": str(ast_path),
                "error_type": "JSONDecodeError",
                "error": f"{exc.msg} at line {exc.lineno}, column {exc.colno}",
            }
        )

    try:
        if hasattr(ATLDocument, "model_validate"):
            ATLDocument.model_validate(payload)
        else:
            ATLDocument.parse_obj(payload)
    except ValidationError as exc:
        return _emit(
            {
                "valid": False,
                "file": str(ast_path),
                "error_type": "ValidationError",
                "error": str(exc),
                "errors": exc.errors(),
            }
        )
    except Exception as exc:
        return _emit(
            {
                "valid": False,
                "file": str(ast_path),
                "error_type": exc.__class__.__name__,
                "error": str(exc),
            }
        )

    return _emit(
        {
            "valid": True,
            "file": str(ast_path),
            "model": "ATLDocument",
            "message": "PASS",
        }
    )


if __name__ == "__main__":
    raise SystemExit(main())
