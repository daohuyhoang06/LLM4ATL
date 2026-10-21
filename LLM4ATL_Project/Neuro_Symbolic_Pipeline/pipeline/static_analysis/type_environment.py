from typing import List, Dict
from common.atl_identifiers import atl_identifier_error
from .errors import SemanticError

class TypeEnvironment:

    def __init__(self, context_class=None, registry=None):
        self.scopes: List[Dict[str, str]] = [{}]  # Danh sách các scope, mỗi scope là một dict
        # Flow-sensitive types for stable expression paths such as
        # ``self.contents``.  Keep these in scopes parallel to variable scopes
        # so a refinement made inside an if/and guard cannot leak outside the
        # guarded expression.
        self.expression_type_scopes: List[Dict[str, str]] = [{}]
        self.context_class = context_class  # Lớp hiện tại đang được kiểm tra
        self.registry = registry  # Registry để truy vấn thông tin kiểu

        self.helpers = {}  # Dictionary để lưu trữ thông tin về các helper
        self.rules = {}  # Dictionary để lưu trữ thông tin về các rule

        self.bind_variable("thisModule", "Module", allow_builtin=True)

        if context_class is not None:
            self.bind_variable("self", context_class, allow_builtin=True)

    def bind_variable(self, name: str, type_name: str, *, allow_builtin: bool = False):
        identifier_error = atl_identifier_error(name, allow_builtin=allow_builtin)
        if identifier_error is not None:
            raise SemanticError(
                f"Invalid ATL variable name '{name}': {identifier_error}. "
                "Rename it consistently in its declaration and references."
            )
        self.scopes[-1][name] = type_name if type_name is not None else "Unknown"

    def lookup_variable(self, name: str) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                val = scope[name]
                return val if val is not None else "Unknown"

        raise SemanticError(
            f"Unknown variable: '{name}'"
        )

    def bind_expression_type(self, expression_path: str, type_name: str):
        """Refine the type of a stable expression path in the current scope."""
        self.expression_type_scopes[-1][expression_path] = (
            type_name if type_name is not None else "Unknown"
        )

    def lookup_expression_type(self, expression_path: str):
        """Return a scoped expression refinement, or ``None`` if absent."""
        root_variable = expression_path.split(".", 1)[0]
        for index in range(len(self.expression_type_scopes) - 1, -1, -1):
            refinements = self.expression_type_scopes[index]
            if expression_path in refinements:
                return refinements[expression_path]

            # A same-named variable declared in a nested scope denotes a new
            # expression path, so refinements attached to the outer variable
            # must not be reused.
            if root_variable in self.scopes[index]:
                return None
        return None

    def push_scope(self):
        self.scopes.append({})
        self.expression_type_scopes.append({})

    def pop_scope(self):
        if len(self.scopes) <= 1:
            raise SemanticError(
                "Cannot pop global scope"
            )

        self.scopes.pop()
        self.expression_type_scopes.pop()

    def register_helper(self, name: str, parameter_types: List[str], return_type: str, context_type: str = None, kind: str = "operation"):
        identifier_error = atl_identifier_error(name)
        if identifier_error is not None:
            raise SemanticError(
                f"Invalid ATL helper name '{name}': {identifier_error}."
            )

        signature = {
            "parameter_types": parameter_types,
            "return_type": return_type,
            "context_type": context_type,
            "kind": kind
        }

        overloads = self.helpers.setdefault(name, [])
        for existing in overloads:
            if (
                existing["parameter_types"] == parameter_types
                and existing["context_type"] == context_type
                and existing["kind"] == kind
            ):
                raise SemanticError(
                    f"Duplicate helper signature: '{name}' "
                    f"for context '{context_type or 'Module'}'"
                )

        overloads.append(signature)

    def lookup_helper(self, name: str):
        if name not in self.helpers:
            raise SemanticError(
                f"Unknown helper: '{name}'"
            )

        return self.helpers[name]

    def register_rule(
        self,
        name: str,
        parameter_types: List[str],
        output_types: List[str],
        rule_kind: str,
        output_variables: Dict[str, str] | None = None,
    ):
        identifier_error = atl_identifier_error(name)
        if identifier_error is not None:
            raise SemanticError(
                f"Invalid ATL rule name '{name}': {identifier_error}."
            )

        if name in self.rules:
            raise SemanticError(
                f"Duplicate rule name: '{name}'"
            )

        self.rules[name] = {
            "parameter_types": parameter_types,
            "output_types": output_types,
            "output_variables": dict(output_variables or {}),
            "rule_kind": rule_kind
        }

    def lookup_rule(self, name: str):
        if name not in self.rules:
            raise SemanticError(
                f"Unknown rule: '{name}'"
            )

        return self.rules[name]
