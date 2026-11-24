"""Build the system and user prompts for ATL generation and repair."""

import json
from pathlib import Path


def load_system_prompt(template_path: Path, schema: dict) -> str:
    """Insert the AST JSON schema into the system prompt template."""
    template = template_path.read_text(encoding="utf-8")
    schema_json = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    return template.replace("<INSERT_SCHEMA_HERE>", schema_json)


def build_prompt(prompt_content, model_content, validation_error=""):
    """Build the user-level input; system guidance is sent separately."""
    prompt = f"=== ECORE MODELS ===\n{model_content}\n\n=== TRANSFORMATION REQUEST ===\n{prompt_content}"
    if validation_error:
        prompt += ("\n\n=== PREVIOUS ATTEMPT FAILED VALIDATION OR FORMAL VERIFICATION ===\n"
                   "Repair the AST and return JSON only. Details:\n"
                   f"{validation_error}")
    return prompt
