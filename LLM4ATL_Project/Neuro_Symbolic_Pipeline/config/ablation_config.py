"""Shared ablation switches for pipeline validation/generation layers.

Set switches in `.env` with the `ABLATION_` prefix, for example:

ABLATION_ENABLE_LAYER1_SCHEMA=false
ABLATION_ENABLE_LAYER2_SEMANTIC=true
ABLATION_ENABLE_LAYER2_TYPE_CHECK=false
ABLATION_ENABLE_LAYER2_EXISTENCE_CHECK=true
ABLATION_ENABLE_LAYER3_GENERATION=true
"""

from dataclasses import dataclass, fields
from os import getenv
from typing import Any, ClassVar


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return True

    normalized = str(value).strip().lower()
    if normalized in {"0", "false", "no", "off", "disabled"}:
        return False
    if normalized in {"1", "true", "yes", "on", "enabled"}:
        return True

    raise ValueError(f"Invalid boolean value for ablation config: {value!r}")


@dataclass(frozen=True)
class AblationConfig:
    enable_layer1_schema: bool = True
    enable_layer2_semantic: bool = True
    enable_layer2_type_check: bool = True
    enable_layer2_existence_check: bool = True
    enable_layer2_null_safety: bool = True
    enable_layer3_generation: bool = True

    _ALIASES: ClassVar[dict[str, str]] = {
        "enable_layer1": "enable_layer1_schema",
        "enable_layer1_validation": "enable_layer1_schema",
        "enable_layer2": "enable_layer2_semantic",
        "enable_layer2_property_check": "enable_layer2_existence_check",
        "enable_layer3": "enable_layer3_generation",
    }

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "AblationConfig":
        if not values:
            return cls()

        field_names = {field.name for field in fields(cls)}
        normalized: dict[str, bool] = {}
        for key, value in values.items():
            field_name = cls._ALIASES.get(key, key)
            if field_name in field_names:
                normalized[field_name] = _parse_bool(value)
        return cls(**normalized)

    @classmethod
    def from_env(cls, prefix: str = "ABLATION_") -> "AblationConfig":
        values = {
            field_name: getenv(f"{prefix}{field_name.upper()}")
            for field_name in {field.name for field in fields(cls)}
        }
        return cls.from_mapping(
            {
                key: value
                for key, value in values.items()
                if value is not None
            }
        )

    def is_enabled(self, name: str) -> bool:
        if name in {
            "enable_layer2_existence_check",
            "enable_layer2_property_check",
            "enable_layer2_null_safety",
        }:
            return self.enable_layer2_existence_check and self.enable_layer2_null_safety

        field_name = self._ALIASES.get(name, name)
        return getattr(self, field_name, True)


DEFAULT_ABLATION_CONFIG = AblationConfig()


def is_enabled(config: AblationConfig | None, name: str) -> bool:
    if config is None:
        return True
    return config.is_enabled(name)
