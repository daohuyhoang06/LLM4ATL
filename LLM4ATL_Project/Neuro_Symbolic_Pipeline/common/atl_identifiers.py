import re
from typing import Optional


# Keywords from the ATL 4.12 concrete syntax used by ATL_Parser. Keep their
# original spelling because ATL keywords are case-sensitive.
ATL_RESERVED_WORDS = frozenset({
    "module", "create", "refining", "from", "library", "query", "uses",
    "helper", "def", "context", "nodefault", "abstract", "rule", "extends",
    "using", "unique", "lazy", "entrypoint", "endpoint", "in", "to",
    "mapsTo", "distinct", "foreach", "drop", "do", "if", "then", "else",
    "endif", "for", "iterate", "super", "let", "true", "false",
    "OclUndefined", "Bag", "Set", "OrderedSet", "Sequence", "Map", "Tuple",
    "OclType", "OclAny", "TupleType", "Integer", "Real", "Boolean", "String",
    "Collection", "not", "div", "mod", "and", "or", "xor", "implies",
})

# These tokens are lexically valid, but declaring them would shadow ATL/OCL's
# predefined receivers and make a generated transformation ambiguous.
ATL_BUILTIN_IDENTIFIERS = frozenset({"self", "thisModule"})

ATL_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def atl_identifier_error(name: str, *, allow_builtin: bool = False) -> Optional[str]:
    """Return why *name* cannot be emitted as an unquoted ATL identifier."""
    if not isinstance(name, str) or not name:
        return "it is empty"
    if ATL_IDENTIFIER_RE.fullmatch(name) is None:
        return "it must match [A-Za-z_][A-Za-z0-9_]*"
    if name in ATL_RESERVED_WORDS:
        return "it is an ATL/OCL reserved word"
    if not allow_builtin and name in ATL_BUILTIN_IDENTIFIERS:
        return "it is an ATL/OCL built-in identifier"
    return None


def is_valid_atl_identifier(name: str, *, allow_builtin: bool = False) -> bool:
    return atl_identifier_error(name, allow_builtin=allow_builtin) is None
