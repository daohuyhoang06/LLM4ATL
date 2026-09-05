from typing import List, Dict
from .errors import SemanticError

class TypeEnvironment:

    def __init__(self, context_class=None, registry=None):
        self.scopes: List[Dict[str, str]] = [{}]  # Danh sách các scope, mỗi scope là một dict
        self.context_class = context_class  # Lớp hiện tại đang được kiểm tra
        self.registry = registry  # Registry để truy vấn thông tin kiểu

        self.helpers = {}  # Dictionary để lưu trữ thông tin về các helper
        self.rules = {}  # Dictionary để lưu trữ thông tin về các rule

        self.bind_variable("thisModule", "Module")

        if context_class is not None:
            self.bind_variable("self", context_class)

    def bind_variable(self, name: str, type_name: str):
        self.scopes[-1][name] = type_name if type_name is not None else "Unknown"

    def lookup_variable(self, name: str) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                val = scope[name]
                return val if val is not None else "Unknown"

        raise SemanticError(
            f"Unknown variable: '{name}'"
        )

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) <= 1:
            raise SemanticError(
                "Cannot pop global scope"
            )

        self.scopes.pop()

    def register_helper(self, name: str, parameter_types: List[str], return_type: str, context_type: str = None, kind: str = "operation"):
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

    def register_rule(self, name: str, parameter_types: List[str], output_types: List[str], rule_kind: str):
        if name in self.rules:
            raise SemanticError(
                f"Duplicate rule name: '{name}'"
            )

        self.rules[name] = {
            "parameter_types": parameter_types,
            "output_types": output_types,
            "rule_kind": rule_kind
        }

    def lookup_rule(self, name: str):
        if name not in self.rules:
            raise SemanticError(
                f"Unknown rule: '{name}'"
            )

        return self.rules[name]
