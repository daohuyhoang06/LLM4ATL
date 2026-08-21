from typing import Optional
import re
from schema.ocl_ast import OCLExpression
from ablation_config import is_enabled
from .type_environment import TypeEnvironment
from .errors import SemanticError
from .ecore_registry import ATLEcoreRegistry

class OCLSemanticChecker:

    @classmethod
    def check(cls, expr: OCLExpression, env: TypeEnvironment,
              ablation_config=None) -> str:

        if not is_enabled(ablation_config, "enable_layer2_semantic"):
            return "Unknown"

        node_type = expr.type

        if node_type == "LiteralExpression":
            return cls._check_literal(expr)

        elif node_type == "CollectionLiteral":
            return cls._check_collection_literal(expr)

        elif node_type == "Variable":
            if "!" in expr.name:
                return expr.name
            return env.lookup_variable(expr.name)

        elif node_type == "PropertyCall":
            return cls._check_property_call(expr, env, ablation_config)

        elif node_type == "OperationCall":
            return cls._check_operation_call(expr, env, ablation_config)

        elif node_type == "BinaryExpression":
            return cls._check_binary_expr(expr, env, ablation_config)

        elif node_type == "UnaryExpression":
            return cls._check_unary_expr(expr, env, ablation_config)

        elif node_type == "IteratorExpression":
            return cls._check_iterator(expr, env, ablation_config)

        elif node_type == "CollectionOperation":
            return cls._check_collection_op(expr, env, ablation_config)

        elif node_type == "IfExpression":
            return cls._check_if_expr(expr, env, ablation_config)

        elif node_type == "LetExpression":
            return cls._check_let_expr(expr, env, ablation_config)

        raise SemanticError(
            f"Unknown node type: {node_type}"
        )


    @classmethod
    def _check_literal(cls, expr) -> str:
        lt = expr.literal_type
        if lt == "String": return "String"
        if lt == "Integer": return "Integer"
        if lt == "Real": return "Real"
        if lt == "Boolean": return "Boolean"
        if lt == "Null": return "Null"
        raise SemanticError(f"Unknown literal: {lt}")


    @classmethod
    def _check_collection_literal(cls, expr) -> str:
        kind = expr.collection_kind
        if kind == "Set": return "Set"
        if kind == "Bag": return "Bag"
        raise SemanticError(f"Unknown collection kind: {kind}")


    @classmethod
    def _check_property_call(cls, expr, env, ablation_config=None) -> str:
        source_type = cls.check(expr.source, env, ablation_config=ablation_config)
        prop_name = expr.property_name

        if prop_name in ("oclIsUndefined", "oclIsNew"):
            return "Boolean"

        if source_type == "Unknown":
            return "Unknown"

        if source_type == "Null":
            if is_enabled(ablation_config, "enable_layer2_existence_check"):
                raise SemanticError(
                    f"Cannot access property '{prop_name}' on Null."
                )
            return "Unknown"

        if source_type == "OclType" and prop_name == "name":
            return "String"

        if prop_name in env.helpers:
            helper = env.helpers[prop_name]
            context_type = helper["context_type"]
            if helper.get("kind") == "attribute":
                if source_type == "Module" and context_type is None:
                    return helper["return_type"]
                if source_type == context_type:
                    return helper["return_type"]

        if env.registry is None:
            if is_enabled(ablation_config, "enable_layer2_existence_check"):
                raise SemanticError(
                    "Registry is not set in the type environment."
                )
            return "Unknown"

        try:
            raw_type = env.registry.resolve_property(source_type, prop_name)
        except SemanticError :
            if is_enabled(ablation_config, "enable_layer2_existence_check"):
                raise SemanticError(
                    f"Property '{prop_name}' not found in type '{source_type}'."
                )
            return "Unknown"

        if re.match(r'^(Set|Bag|Sequence|OrderedSet)\(([^)]+)\)$', raw_type):
            return raw_type

        clean_type = re.sub(r'\[.*\]$', '', raw_type).strip()

        return clean_type

    @classmethod
    def _check_operation_call(cls, expr, env, ablation_config=None) -> str:
        source_type = cls.check(expr.source, env, ablation_config=ablation_config)
        op = expr.operation_name

        if source_type == "Null" and op != "oclIsUndefined":
            if is_enabled(ablation_config, "enable_layer2_existence_check"):
                raise SemanticError(
                    f"Cannot call operation '{op}' on Null."
                )
            return "Unknown"

        if op == "allInstances": return f"Set({source_type})"
        if op == "size": return "Integer"
        if op == "isEmpty": return "Boolean"
        if op == "notEmpty": return "Boolean"
        if op == "sum": return "Integer"
        if op == "flatten": return source_type
        if op == "asSet": 
            inner = cls._element_type(source_type)
            return f"Set({inner})" if inner != "Unknown" else "Set"
        if op == "asBag": 
            inner = cls._element_type(source_type)
            return f"Bag({inner})" if inner != "Unknown" else "Bag"
        if op == "asSequence": 
            inner = cls._element_type(source_type)
            return f"Sequence({inner})" if inner != "Unknown" else "Sequence"
        if op == "asOrderedSet": 
            inner = cls._element_type(source_type)
            return f"OrderedSet({inner})" if inner != "Unknown" else "OrderedSet"
        if op in ("first", "last", "at"):
            return cls._element_type(source_type)
        if op == "indexOf": return "Integer"
        if op == "count": return "Integer"
        if op == "includes": return "Boolean"
        if op == "excludes": return "Boolean"
        if op in ("includesAll", "excludesAll"): return "Boolean"
        if op in ("union", "intersection", "symmetricDifference"):
            return source_type
        if op in ("select", "reject"): return source_type
        if op == "collect": return "Bag"
        if op in ("forAll", "exists", "isUnique"): return "Boolean"
        if op == "oclIsUndefined": return "Boolean"
        if op in ("oclIsTypeOf", "oclIsKindOf"):
            if len(expr.arguments) != 1:
                raise SemanticError(f"{op} expects exactly one argument")

            target = expr.arguments[0]
            if target.type != "Variable" or "!" not in target.name:
                raise SemanticError(f"{op} expects a metamodel type argument")

            return "Boolean"
        if op == "oclAsType":
            if len(expr.arguments) != 1:
                raise SemanticError("oclAsType expects exactly one argument")

            target = expr.arguments[0]
            if target.type == "Variable" and "!" in target.name:
                return target.name
            
            return "Unknown"

        if op == "oclType": return "OclType"
        if op == "resolveTemp":
            if source_type != "Module":
                raise SemanticError("resolveTemp must be called through thisModule")
            if len(expr.arguments) != 2:
                raise SemanticError("resolveTemp expects exactly two arguments")

            cls.check(expr.arguments[0], env, ablation_config=ablation_config)
            target_name_type = cls.check(expr.arguments[1], env, ablation_config=ablation_config)
            if is_enabled(ablation_config, "enable_layer2_type_check") and target_name_type not in ("String", "Unknown"):
                raise SemanticError(f"resolveTemp target name must be String, got {target_name_type}")
            return "Unknown"
        if op == "toString": return "String"
        if op == "abs": return source_type
        if op == "floor": return "Integer"
        if op == "round": return "Integer"
        if op == "div": return "Integer"
        if op == "mod": return "Integer"
        if op == "max": return source_type
        if op == "min": return source_type
        if op == "toInteger": return "Integer"
        if op == "toReal": return "Real"
        if op == "toUpperCase": return "String"
        if op == "toLowerCase": return "String"
        if op == "substring": return "String"
        if op == "concat": return "String"
        if op == "startsWith": return "Boolean"
        if op == "endsWith": return "Boolean"
        if op == "indexOf": return "Integer"


        if op in env.helpers:

            helper = env.helpers[op]
            context_type = helper["context_type"]

            if source_type == "Module":
                if context_type is None:
                    pass

                else:
                    raise SemanticError(
                        f"Context helper '{op}' cannot be called "
                        f"through thisModule"
                    )

            else:
                if context_type is None:
                    raise SemanticError(
                        f"Module helper '{op}' must be called through thisModule"
                    )

                if source_type != "Unknown" and not cls._is_type_compatible(source_type, context_type, env):
                    raise SemanticError(
                        f"Helper '{op}' cannot be called on "
                        f"'{source_type}', expected '{context_type}'"
                    )

            cls._check_call_arguments(name=op, arguments=expr.arguments, parameter_types=helper["parameter_types"], env=env, ablation_config=ablation_config)

            return helper["return_type"]

        
        if op in env.rules:
            rule = env.rules[op]

            cls._check_call_arguments(name=op, arguments=expr.arguments, parameter_types=rule["parameter_types"], env=env, ablation_config=ablation_config)

            output_types = rule["output_types"]

            if len(output_types) == 1:
                return output_types[0]

            return "Unknown"
            
        if is_enabled(ablation_config, "enable_layer2_existence_check"):
            raise SemanticError(
                 f"Unknown helper or rule: '{op}'"
            )
        return "Unknown"

    @classmethod
    def _check_call_arguments(cls, name: str, arguments: list, parameter_types: list, env, ablation_config=None):

        if len(arguments) != len(parameter_types):
            raise SemanticError(
                f"Argument count mismatch for '{name}': expected {len(parameter_types)}, got {len(arguments)}"
            )

        for argument, expected_type in zip(arguments, parameter_types):

            actual_type = cls.check(argument, env, ablation_config=ablation_config)

            if actual_type == "Unknown" or expected_type is None:
                continue

            if is_enabled(ablation_config, "enable_layer2_type_check") and not cls._is_type_compatible(actual_type, expected_type, env):
                    raise SemanticError(
                        f"Argument type mismatch for '{name}': expected {expected_type}, got {actual_type}"
                    )

    @classmethod
    def _check_binary_expr(cls, expr, env, ablation_config=None) -> str:
        op = expr.operator
        left_type = cls.check(expr.left, env, ablation_config=ablation_config)

        if op == "and":
            env.push_scope()
            try:
                cls._apply_guard_type_refinements(expr.left, env)
                right_type = cls.check(expr.right, env, ablation_config=ablation_config)
            finally:
                env.pop_scope()
        else:
            right_type = cls.check(expr.right, env, ablation_config=ablation_config)

        if not is_enabled(ablation_config, "enable_layer2_type_check"):

            pass
        else:
            if op in ('=', '<>'):

                if left_type != right_type and left_type != "Unknown" and right_type != "Unknown":

                    if (
                        not ({left_type, right_type} <= {"Integer", "Real"})
                        and not cls._is_type_compatible(left_type, right_type, env)
                        and not cls._is_type_compatible(right_type, left_type, env)
                    ):
                        raise SemanticError(
                            f"Can't compare: '{left_type}' {op} '{right_type}'"
                        )
            elif op in ('<', '>', '<=', '>='):

                if left_type != right_type and left_type != "Unknown" and right_type != "Unknown":

                    if not ({left_type, right_type} <= {"Integer", "Real"}):
                        raise SemanticError(
                            f"Can't compare: '{left_type}' {op} '{right_type}'"
                        )
            elif op in ('+', '-', '*', '/'):
                
                if op == '+' and left_type == "String" and right_type == "String":
                    pass # String concatenation allowed
                else:
                    if left_type not in ("Integer", "Real", "Unknown", "String") or (left_type == "String" and op != '+'):
                        raise SemanticError(
                            f" '{op}' can't be used for '{left_type}'"
                        )
                    if right_type not in ("Integer", "Real", "Unknown", "String") or (right_type == "String" and op != '+'):
                        raise SemanticError(
                            f" '{op}' can't be used for '{right_type}'"
                        )
            elif op in ('and', 'or', 'xor', 'implies'):
                if left_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f" '{op}' can't be used for '{left_type}'"
                    )
                if right_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f" '{op}' can't be used for '{right_type}'"
                    )

        if op in ('=', '<>', '<', '>', '<=', '>='):
            return "Boolean"
        elif op in ('and', 'or', 'xor', 'implies'):
            return "Boolean"
        elif op in ('+', '-', '*', '/'):
            if op == '+' and left_type == "String" and right_type == "String":
                return "String"
            if left_type == "Real" or right_type == "Real":
                return "Real"
            return "Integer"
        elif op == 'div' or op == 'mod':
            return "Integer"

        return "Unknown"

    @classmethod
    def _apply_guard_type_refinements(cls, expr, env) -> None:
        if expr is None:
            return

        if expr.type == "BinaryExpression" and expr.operator == "and":
            cls._apply_guard_type_refinements(expr.left, env)
            cls._apply_guard_type_refinements(expr.right, env)
            return

        if expr.type != "OperationCall" or expr.operation_name not in ("oclIsKindOf", "oclIsTypeOf"):
            return

        if len(expr.arguments) != 1:
            return

        source = expr.source
        target = expr.arguments[0]
        if source.type == "Variable" and target.type == "Variable" and "!" in target.name:
            env.bind_variable(source.name, target.name)


    @classmethod
    def _check_unary_expr(cls, expr, env, ablation_config=None) -> str:
        operand_type = cls.check(expr.expression, env, ablation_config=ablation_config)
        op = expr.operator

        if op == "not":

            if not is_enabled(ablation_config, "enable_layer2_type_check"):
                pass
            else:
                if operand_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f"'not' can't be used for '{operand_type}'"
                    )
            return "Boolean"
        elif op == "-":
            if not is_enabled(ablation_config, "enable_layer2_type_check"):
                pass
            else:
                if operand_type not in ("Integer", "Real", "Unknown"):
                    raise SemanticError(
                        f" '-' can't be used for '{operand_type}'"
                    )
            if operand_type == "Real":
                return "Real"
            return "Integer"

        raise SemanticError(f"Unknown operation '{op}'")


    @classmethod
    def _check_iterator(cls, expr, env, ablation_config=None) -> str:
        source_type = cls.check(expr.source, env, ablation_config=ablation_config)
        iter_type = expr.iterator_type
        element_type = cls._element_type(source_type)

        env.push_scope()
        try:
            for it in expr.iterators:
                env.bind_variable(it.name, element_type)
            body_type = cls.check(expr.body, env, ablation_config=ablation_config)
        finally:
            env.pop_scope()

        if iter_type in ("forAll", "exists"):

            if not is_enabled(ablation_config, "enable_layer2_type_check"):
                pass
            else:
                if body_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f"{iter_type} should be Boolean, but not {body_type}"
                    )
            return "Boolean"

        elif iter_type in ("select", "reject"):
            if not is_enabled(ablation_config, "enable_layer2_type_check"):
                pass
            else:
                if body_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f"{iter_type} should be Boolean, but not {body_type}"
                    )
            if iter_type == "select":
                refined_type = cls._select_refined_collection_type(expr, source_type, element_type, env)
                if refined_type is not None:
                    return refined_type
            return source_type

        elif iter_type == "collect":
            if source_type.startswith("Sequence") or source_type.startswith("OrderedSet"):
                return f"Sequence({body_type})" if body_type != "Unknown" else "Sequence"
            else:
                return f"Bag({body_type})" if body_type != "Unknown" else "Bag"

        elif iter_type == "isUnique":
            if not is_enabled(ablation_config, "enable_layer2_type_check"):
                pass
            else:
                if cls.is_collection_type(body_type):
                    raise SemanticError(
                        f"isUnique can't be used for {body_type}"
                    )
            return "Boolean"

        elif iter_type == "sortedBy":
            if source_type.startswith("Set"):
                return f"OrderedSet({element_type})" if element_type != "Unknown" else "OrderedSet"
            else:
                return f"Sequence({element_type})" if element_type != "Unknown" else "Sequence"

        elif iter_type == "any":
            if not is_enabled(ablation_config, "enable_layer2_type_check"):
                pass
            else:
                if body_type not in ("Boolean", "Unknown"):
                    raise SemanticError(f"Condition for 'any' must be Boolean, got {body_type}")
            return element_type

        raise SemanticError(
            f"Unknown iterator type '{iter_type}'. "
            f"So far only forAll, exists, select, reject, collect, isUnique, sortedBy, any are supported"
        )


    @classmethod
    def _check_collection_op(cls, expr, env, ablation_config=None) -> str:
        source_type = cls.check(expr.source, env, ablation_config=ablation_config)
        op = expr.operation_name

        if op == "size": return "Integer"
        if op == "isEmpty": return "Boolean"
        if op == "notEmpty": return "Boolean"
        if op == "sum": return "Integer"
        if op in ("first", "last"):
            return cls._element_type(source_type)
        if op == "at":
            if len(expr.arguments) != 1:
                raise SemanticError("at expects exactly one argument")
            index_type = cls.check(expr.arguments[0], env, ablation_config=ablation_config)
            if is_enabled(ablation_config, "enable_layer2_type_check") and index_type not in ("Integer", "Unknown"):
                raise SemanticError(f"at index must be Integer, got {index_type}")
            return cls._element_type(source_type)
        if op == "includes": return "Boolean"
        if op == "excludes": return "Boolean"
        if op in ("includesAll", "excludesAll"): return "Boolean"
        if op in ("union", "intersection", "symmetricDifference"):
            return source_type
        if op == "flatten": return source_type
        if op == "asSet": 
            inner = cls._element_type(source_type)
            return f"Set({inner})" if inner != "Unknown" else "Set"
        if op == "asBag": 
            inner = cls._element_type(source_type)
            return f"Bag({inner})" if inner != "Unknown" else "Bag"
        if op == "count": return "Integer"

        return "Unknown"


    @classmethod
    def _check_if_expr(cls, expr, env, ablation_config=None) -> str:
        cond_type = cls.check(expr.condition, env, ablation_config=ablation_config)
        then_type = cls.check(expr.then_expression, env, ablation_config=ablation_config)
        else_type = cls.check(expr.else_expression, env, ablation_config=ablation_config)


        if not is_enabled(ablation_config, "enable_layer2_type_check"):
            pass
        else:
            if cond_type not in ("Boolean", "Unknown"):
                raise SemanticError(
                    f"If condition should be Boolean but not {cond_type}"
                )

        if then_type == else_type:
            return then_type
        if then_type == "Unknown": return else_type
        if else_type == "Unknown": return then_type

        if {then_type, else_type} <= {"Integer", "Real"}:
            return "Real"
        return then_type


    @classmethod
    def _check_let_expr(cls, expr, env, ablation_config=None) -> str:
        declared_type = expr.variable.declared_type
        if not declared_type or not str(declared_type).strip():
            raise SemanticError(f"Let variable '{expr.variable.name}' is missing declared type.")
        declared_type = str(declared_type).strip()

        val_type = cls.check(expr.value, env, ablation_config=ablation_config)

        if not is_enabled(ablation_config, "enable_layer2_type_check"):
            pass
        else:
            if val_type != "Unknown" and declared_type not in cls._compatible_types(val_type):
                raise SemanticError(
                    f"Let declared '{expr.variable.name}' as {declared_type},"
                    f"but now it's {val_type}"
                )
        env.push_scope()
        try:
            env.bind_variable(expr.variable.name, declared_type)
            body_type = cls.check(expr.body, env, ablation_config=ablation_config)
        finally:
            env.pop_scope()
        return body_type


    @classmethod
    def _element_type(cls, coll_type: str) -> str:

        match = re.match( r'(Set|Bag|Sequence|OrderedSet)\(([^)]+)\)', coll_type)
        if match:
            return match.group(2)
        return "Unknown"

    @classmethod
    def _select_refined_collection_type(cls, expr, source_type: str, element_type: str, env) -> str:
        match = re.match(r'^(Set|Bag|Sequence|OrderedSet)\(([^)]+)\)$', source_type)
        if not match or len(expr.iterators) != 1:
            return None

        body = expr.body
        if body.type != "OperationCall" or body.operation_name not in ("oclIsKindOf", "oclIsTypeOf"):
            return None

        source = body.source
        target = body.arguments[0] if len(body.arguments) == 1 else None
        iterator_name = expr.iterators[0].name
        if source.type != "Variable" or source.name != iterator_name:
            return None
        if target is None or target.type != "Variable" or "!" not in target.name:
            return None

        if element_type != "Unknown" and not cls._is_type_compatible(target.name, element_type, env):
            return None

        return f"{match.group(1)}({target.name})"

    @classmethod
    def is_collection_type(cls, type_str: str) -> bool:

        return bool(re.match(r'(Set|Bag|Sequence|OrderedSet)', type_str))

    @classmethod
    def _compatible_types(cls, derived_type: str) -> set:

        compatibility_map = {
            "Integer": {"Integer", "Real"},
            "Real": {"Real"},
            "String": {"String"},
            "Boolean": {"Boolean"},
        }
        return compatibility_map.get(derived_type, {derived_type})
    
    @classmethod
    def _is_type_compatible(cls, actual_type, expected_type, env):
        actual_type = cls._normalize_type(actual_type)
        expected_type = cls._normalize_type(expected_type)

        if actual_type == expected_type:
            return True

        # Primitive compatibility
        if expected_type in cls._compatible_types(actual_type):
            return True

        # Collection compatibility
        src_match = re.match(
            r'^(Set|Bag|Sequence|OrderedSet)\((.+)\)$',
            actual_type
        )
        tgt_match = re.match(
            r'^(Set|Bag|Sequence|OrderedSet)\((.+)\)$',
            expected_type
        )

        if src_match and tgt_match:
            src_collection = src_match.group(1)
            tgt_collection = tgt_match.group(1)

            if src_collection != tgt_collection:
                return False

            return cls._is_type_compatible(
                src_match.group(2),
                tgt_match.group(2),
                env
            )

        # Một bên collection, một bên không
        if src_match or tgt_match:
            return False

        # EClass inheritance
        if env and env.registry:
            src_base = actual_type.split("!")[-1]
            tgt_base = expected_type.split("!")[-1]

            queue = [src_base]
            visited = set()

            while queue:
                current_class = queue.pop(0)
                if current_class in visited:
                    continue
                visited.add(current_class)

                if current_class == tgt_base:
                    return True

                class_info = env.registry.uml_context.get(current_class)

                if not class_info:
                    continue

                for super_cls in class_info.get("super_classes", []):
                    super_base = super_cls.split("!")[-1] if "!" in super_cls else super_cls
                    queue.append(super_base)

        return False

    @staticmethod
    def _normalize_type(type_name: str) -> str:
        if type_name is None:
            return type_name
        return re.sub(r'\[[^\]]+\]$', '', type_name).strip()
