"""Build the system and user prompts used for ATL generation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


_SCHEMA_PLACEHOLDER = "<INSERT_SCHEMA_HERE>"


def build_system_prompt(
    template: str,
    schema: Mapping[str, Any],
) -> str:
    """Insert the compact ATL AST JSON schema into the system template."""
    schema_json = json.dumps(
        schema,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return template.replace(_SCHEMA_PLACEHOLDER, schema_json)


def build_user_prompt(
    *,
    transformation_request: str,
    ecore_models: str,
    forward_tl: str = "",
    validation_error: str = "",
) -> str:
    """Combine the request, metamodels, DSS guidance, and repair feedback."""
    prompt = (
        f"=== ECORE MODELS ===\n{ecore_models}\n\n"
        f"=== TRANSFORMATION REQUEST ===\n{transformation_request}"
    )

    if forward_tl.strip():
        prompt += (
            "\n\n=== AGILEUML DSS STRUCTURAL MAPPING GUIDANCE (forward.tl) ===\n"
            "This mapping was inferred automatically from the requirements and "
            "the two metamodels. Use it as structural guidance, not as the "
            "authoritative transformation specification. It can be incomplete "
            "or contain heuristic mappings. The transformation request above "
            "remains the semantic authority. Only use classes and features that "
            "exist in the supplied Ecore models.\n\n"
            f"{forward_tl.strip()}"
        )

    if validation_error:
        prompt += (
            "\n\n=== PREVIOUS ATTEMPT FAILED VALIDATION OR FORMAL VERIFICATION ===\n"
            "Repair the AST and return JSON only. Details:\n"
            f"{validation_error}"
        )

    return prompt
