from typing import Optional
import re
from schema.ocl_ast import OCLExpression
from .type_environment import TypeEnvironment
from .errors import SemanticError
from .ecore_registry import ATLEcoreRegistry

class OCLSemanticChecker:

    @classmethod
    def check(cls, expr: OCLExpression, env: TypeEnvironment,
              ablation_config=None) -> str:

        if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_semantic"):
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

        if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_null_safety"):
            pass

        prop_name = expr.property_name
        if prop_name in ("oclIsUndefined", "oclIsNew"):
            return "Boolean"

        if source_type == "Unknown":
            return "Unknown"

        if env.registry is None:
            raise SemanticError(
                "Registry is not set in the type environment."
            )

        try:
            raw_type = env.registry.resolve_property(source_type, prop_name)
        except SemanticError :
            raise SemanticError(
                f"Property '{prop_name}' not found in type '{source_type}'."
            )

        if re.match(r'^(Set|Bag|Sequence|OrderedSet)\(([^)]+)\)$', raw_type):
            return raw_type

        clean_type = re.sub(r'\[.*\]$', '', raw_type).strip()

        return clean_type

    @classmethod
    def _check_operation_call(cls, expr, env, ablation_config=None) -> str:
        source_type = cls.check(expr.source, env, ablation_config=ablation_config)
        op = expr.operation_name

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
        if op == "oclIsTypeOf": return "Boolean"
        if op == "oclIsKindOf": return "Boolean"
        if op == "oclAsType": return "Unknown"
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

                if source_type != context_type:
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
            
        raise SemanticError(
             f"Unknown helper or rule: '{op}'"
        )

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

            if not cls._is_type_compatible(actual_type, expected_type, env):
                    raise SemanticError(
                        f"Argument type mismatch for '{name}': expected {expected_type}, got {actual_type}"
                    )

    @classmethod
    def _check_binary_expr(cls, expr, env, ablation_config=None) -> str:
        left_type = cls.check(expr.left, env, ablation_config=ablation_config)
        right_type = cls.check(expr.right, env, ablation_config=ablation_config)
        op = expr.operator

        if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):

            pass
        else:
            if op in ('=', '<>', '<', '>', '<=', '>='):

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
    def _check_unary_expr(cls, expr, env, ablation_config=None) -> str:
        operand_type = cls.check(expr.expression, env, ablation_config=ablation_config)
        op = expr.operator

        if op == "not":

            if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
                pass
            else:
                if operand_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f"'not' can't be used for '{operand_type}'"
                    )
            return "Boolean"
        elif op == "-":
            if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
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

            if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
                pass
            else:
                if body_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f"{iter_type} should be Boolean, but not {body_type}"
                    )
            return "Boolean"

        elif iter_type in ("select", "reject"):
            if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
                pass
            else:
                if body_type not in ("Boolean", "Unknown"):
                    raise SemanticError(
                        f"{iter_type} should be Boolean, but not {body_type}"
                    )
            return source_type

        elif iter_type == "collect":
            if source_type.startswith("Sequence") or source_type.startswith("OrderedSet"):
                return f"Sequence({body_type})" if body_type != "Unknown" else "Sequence"
            else:
                return f"Bag({body_type})" if body_type != "Unknown" else "Bag"

        elif iter_type == "isUnique":
            if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
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
            if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
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


        if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
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
        val_type = cls.check(expr.value, env, ablation_config=ablation_config)


        if ablation_config is not None and not ablation_config.is_enabled("enable_layer2_type_check"):
            pass
        else:
            if expr.variable.declared_type and val_type != "Unknown" and expr.variable.declared_type not in cls._compatible_types(val_type):
                raise SemanticError(
                    f"Let declared '{expr.variable.name}' as {expr.variable.declared_type},"
                    f"but now it's {val_type}"
                )
        env.push_scope()
        try:
            env.bind_variable(expr.variable.name, val_type)
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

            current_class = src_base

            while current_class:
                if current_class == tgt_base:
                    return True

                class_info = env.registry.uml_context.get(current_class)

                if not class_info:
                    break

                current_class = class_info.get("super_class")

        return False