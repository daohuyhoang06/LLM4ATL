"""Provider adapter for the neuro-symbolic pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


class LLMConfigurationError(RuntimeError):
    """Raised when the selected provider cannot be configured."""


_DEFAULT_MODELS = {
    "gemini": "gemini-3.5-flash",
    "openai": "gpt-5.1",
    "claude": "claude-sonnet-4-5",
}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _required_key(provider: str, name: str) -> str:
    value = _clean(os.getenv(name))
    if not value or value.startswith("your_"):
        raise LLMConfigurationError(
            f"Thiếu {name}. Hãy đặt API key cho provider '{provider}' trong file .env."
        )
    return value


def _positive_int_env(name: str, default: int) -> int:
    """Read a positive integer environment variable with a clear error."""
    raw_value = _clean(os.getenv(name, str(default)))
    try:
        value = int(raw_value)
    except ValueError as error:
        raise LLMConfigurationError(f"{name} must be a positive integer.") from error
    if value <= 0:
        raise LLMConfigurationError(f"{name} must be greater than 0.")
    return value


@dataclass
class LLMClient:
    """Provider-neutral text generation client."""

    provider: str
    model_name: str
    client: Any

    def generate(self, prompt: str, instructions: str = "") -> str:
        """Generate a response from a user prompt and optional system instructions.

        OpenAI and Anthropic expose native fields for system-level guidance.
        The legacy Gemini SDK used here does not, so it retains the previous
        behaviour of prefixing that guidance to the request text.
        """
        if self.provider == "gemini":
            request_text = f"{instructions}\n\n{prompt}" if instructions else prompt
            response = self.client.generate_content(request_text)
            text = getattr(response, "text", None)
        elif self.provider == "openai":
            reasoning_effort = _clean(os.getenv("OPENAI_REASONING_EFFORT", "medium")).lower()
            if reasoning_effort not in {"none", "low", "medium", "high"}:
                raise LLMConfigurationError(
                    "OPENAI_REASONING_EFFORT phải là: none, low, medium hoặc high."
                )
            request_kwargs = {
                "model": self.model_name,
                "input": prompt,
                "reasoning": {"effort": reasoning_effort},
            }
            if instructions:
                request_kwargs["instructions"] = instructions
            response = self.client.responses.create(
                **request_kwargs,
            )
            text = getattr(response, "output_text", None)
        elif self.provider == "claude":
            # Anthropic requires max_tokens even when the caller only wants
            # to configure a thinking budget. Keep this transport detail
            # internal instead of exposing another .env setting.
            max_tokens = 20_000
            thinking_budget = _positive_int_env(
                "ANTHROPIC_THINKING_BUDGET_TOKENS", 8_192
            )
            if thinking_budget >= max_tokens:
                raise LLMConfigurationError(
                    "ANTHROPIC_THINKING_BUDGET_TOKENS must be lower than 20000."
                )
            request_kwargs = {
                "model": self.model_name,
                "max_tokens": max_tokens,
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": thinking_budget,
                },
                "messages": [{"role": "user", "content": prompt}],
            }
            if instructions:
                request_kwargs["system"] = instructions
            response = self.client.messages.create(
                **request_kwargs,
            )
            text = "".join(
                block.text
                for block in getattr(response, "content", [])
                if getattr(block, "type", None) == "text"
            )
        else:
            raise LLMConfigurationError(f"Provider không được hỗ trợ: {self.provider}")

        if not text or not text.strip():
            raise RuntimeError(
                f"Provider '{self.provider}' trả về response rỗng cho model '{self.model_name}'."
            )
        return text.strip()


def create_llm_client() -> LLMClient:
    """Build the configured provider client from environment variables.

    Supported values for ``LLM_PROVIDER`` are ``gemini``, ``openai`` and
    ``claude``. ``LLM_MODEL`` overrides the provider default.
    """

    provider = _clean(os.getenv("LLM_PROVIDER", "gemini")).lower()
    provider = {"google": "gemini", "anthropic": "claude"}.get(provider, provider)
    if provider not in _DEFAULT_MODELS:
        supported = ", ".join(_DEFAULT_MODELS)
        raise LLMConfigurationError(
            f"LLM_PROVIDER='{provider}' không hợp lệ. Chọn một trong: {supported}."
        )

    model_name = _clean(os.getenv("LLM_MODEL")) or _clean(
        os.getenv(f"{provider.upper()}_MODEL")
    ) or _DEFAULT_MODELS[provider]

    if provider == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=_required_key(provider, "GEMINI_API_KEY"))
        client = genai.GenerativeModel(model_name)
    elif provider == "openai":
        from openai import OpenAI

        kwargs: dict[str, Any] = {"api_key": _required_key(provider, "OPENAI_API_KEY")}
        base_url = _clean(os.getenv("OPENAI_BASE_URL"))
        if base_url:
            kwargs["base_url"] = base_url
        client = OpenAI(**kwargs)
    else:
        try:
            from anthropic import Anthropic
        except ImportError as error:
            raise LLMConfigurationError(
                "Provider 'claude' cần package 'anthropic'. "
                "Chạy: python -m pip install -r requirements.txt"
            ) from error

        kwargs = {"api_key": _required_key(provider, "ANTHROPIC_API_KEY")}
        base_url = _clean(os.getenv("ANTHROPIC_BASE_URL"))
        if base_url:
            kwargs["base_url"] = base_url
        client = Anthropic(**kwargs)

    return LLMClient(
        provider=provider,
        model_name=model_name,
        client=client,
    )
