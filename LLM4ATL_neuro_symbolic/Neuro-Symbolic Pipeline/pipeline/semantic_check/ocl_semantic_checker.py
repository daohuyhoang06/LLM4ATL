from typing import Optional
import re
from schema.ocl_ast import OCLExpression
from ablation_config import is_enabled
from .type_environment import TypeEnvironment
from .errors import SemanticError
from .ecore_registry import ATLEcoreRegistry


_COLLECTION_OPERATIONS = frozenset({
    "size", "isEmpty", "notEmpty", "sum", "first", "last", "at",
    "includes", "excludes", "includesAll", "excludesAll", "union",
    "intersection", "symmetricDifference", "flatten", "asSet", "asBag",
    "count",
})


class OCLSemanticChecker:

    @classmethod
    def check(cls, expr: OCLExpression, env: TypeEnvironment,
              ablation_config=None) -> str:

        if not is_enabled(ablation_config, "enable_layer2_semantic"):
            return "Unknown"

        node_type = expr.type

        if node_type == "LiteralExpression":
            return cls._check_literal(expr)

        elif node_type == "OclUndefined":
            return "Null"

        elif node_type == "EnumLiteral":
            return "Unknown"

        elif node_type == "CollectionLiteral":
            return cls._check_collection_literal(expr)

        elif node_type == "Variable":
            # Backward compatibility for ASTs generated before OclUndefined had
            # its own node type.
            if expr.name == "OclUndefined":
                return "Null"
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
        if kind not in ("Set", "Bag"):
            raise SemanticError(f"Unknown collection kind: {kind}")

        # An empty collection has no element from which to infer its type.
        # Keep that uncertainty explicit so it can be unified with the other
        # branch of an if-expression (e.g. Set {} with Set(CPL!Location)).
        if not expr.elements:
            return f"{kind}(Unknown)"

        return kind


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
            applicable_helpers = cls._applicable_helpers(
                env.helpers[prop_name], source_type, env
            )
            attribute_helpers = [
                helper
                for helper in applicable_helpers
                if helper.get("kind") == "attribute"
            ]
            if attribute_helpers:
                helper = cls._select_most_specific_helper(
                    prop_name, attribute_helpers, source_type, env
                )
                return helper["return_type"]
            if applicable_helpers:
                raise SemanticError(
                    f"Helper '{prop_name}' is declared as operation but called "
                    "as an attribute via PropertyCall. Use OperationCall with "
                    f"operation_name='{prop_name}' and arguments=[]."
                )

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

        if op == "refImmediateComposite":
            if len(expr.arguments) != 0:
                raise SemanticError("refImmediateComposite expects no arguments")
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
            return cls._single_collection_element_type(source_type)
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

            resolved_source_type = cls.check(
                expr.arguments[0], env, ablation_config=ablation_config
            )
            target_name_expr = expr.arguments[1]
            target_name_type = cls.check(
                target_name_expr, env, ablation_config=ablation_config
            )
            if is_enabled(ablation_config, "enable_layer2_type_check") and target_name_type not in ("String", "Unknown"):
                raise SemanticError(f"resolveTemp target name must be String, got {target_name_type}")

            # resolveTemp(source, 'label') returns the target-pattern variable
            # identified by label. The environment records those labels while
            # registering rules, so a literal label can be typed without
            # executing the transformation. Dynamic or ambiguous labels keep
            # the previous conservative Unknown result.
            if (
                target_name_expr.type == "LiteralExpression"
                and target_name_expr.literal_type == "String"
                and isinstance(target_name_expr.value, str)
            ):
                candidate_types = set()
                for rule in env.rules.values():
                    output_type = rule.get("output_variables", {}).get(
                        target_name_expr.value
                    )
                    if output_type is None:
                        continue

                    parameter_types = rule.get("parameter_types", [])
                    source_matches = (
                        resolved_source_type == "Unknown"
                        or not parameter_types
                        or any(
                            cls._is_type_compatible(
                                resolved_source_type, parameter_type, env
                            )
                            for parameter_type in parameter_types
                        )
                    )
                    if source_matches:
                        candidate_types.add(output_type)

                if len(candidate_types) == 1:
                    return next(iter(candidate_types))

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
            helpers = env.helpers[op]
            applicable_helpers = cls._applicable_helpers(helpers, source_type, env)
            operation_helpers = [
                helper
                for helper in applicable_helpers
                if helper.get("kind") == "operation"
            ]

            if not applicable_helpers:
                cls._raise_helper_context_error(op, helpers, source_type)

            if not operation_helpers:
                raise SemanticError(
                    f"Helper '{op}' is declared as attribute but called as an "
                    "operation via OperationCall. Use PropertyCall with "
                    f"property_name='{op}'."
                )

            arity_matches = [
                helper
                for helper in operation_helpers
                if len(helper["parameter_types"]) == len(expr.arguments)
            ]
            helper = cls._select_most_specific_helper(
                op,
                arity_matches or operation_helpers,
                source_type,
                env,
            )

            cls._check_call_arguments(name=op, arguments=expr.arguments, parameter_types=helper["parameter_types"], env=env, ablation_config=ablation_config)

            return helper["return_type"]

        
        if op in env.rules:
            rule = env.rules[op]

            if source_type != "Module":
                raise SemanticError(
                    f"Rule '{op}' must be called through thisModule"
                )

            rule_kind = rule["rule_kind"]
            if rule_kind == "MatchedRule":
                raise SemanticError(
                    f"Matched rule '{op}' cannot be called explicitly"
                )

            cls._check_call_arguments(name=op, arguments=expr.arguments, parameter_types=rule["parameter_types"], env=env, ablation_config=ablation_config)

            output_types = rule["output_types"]

            # An explicit lazy-rule invocation evaluates to its default target
            # pattern element: the first element declared in the ``to`` block.
            if rule_kind == "LazyMatchedRule":
                return output_types[0] if output_types else "Unknown"

            # Preserve the existing CalledRule behavior.
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
    def _helper_context_distance(cls, helper: dict, source_type: str, env) -> Optional[int]:
        context_type = helper.get("context_type")

        if source_type == "Module":
            return 0 if context_type is None else None

        if context_type is None:
            return None

        if source_type == "Unknown":
            return 0

        actual_type = cls._normalize_type(source_type)
        expected_type = cls._normalize_type(context_type)
        if env.registry is not None:
            actual_type = env.registry.resolve_class_name(actual_type)
            expected_type = env.registry.resolve_class_name(expected_type)

        if actual_type == expected_type:
            return 0

        if env.registry is not None:
            queue = [(actual_type, 0)]
            visited = set()
            while queue:
                current_type, distance = queue.pop(0)
                if current_type in visited:
                    continue
                visited.add(current_type)

                if current_type == expected_type:
                    return distance

                class_info = env.registry.uml_context.get(current_type, {})
                for super_type in class_info.get("super_classes", []):
                    queue.append((super_type, distance + 1))

        if cls._is_type_compatible(source_type, context_type, env):
            return 1

        return None

    @classmethod
    def _applicable_helpers(cls, helpers: list, source_type: str, env) -> list:
        return [
            helper
            for helper in helpers
            if cls._helper_context_distance(helper, source_type, env) is not None
        ]

    @classmethod
    def _select_most_specific_helper(
        cls,
        name: str,
        helpers: list,
        source_type: str,
        env,
    ) -> dict:
        ranked_helpers = [
            (cls._helper_context_distance(helper, source_type, env), helper)
            for helper in helpers
        ]
        best_distance = min(distance for distance, _ in ranked_helpers)
        best_helpers = [
            helper
            for distance, helper in ranked_helpers
            if distance == best_distance
        ]

        if len(best_helpers) > 1:
            contexts = sorted(
                {helper.get("context_type") or "Module" for helper in best_helpers}
            )
            raise SemanticError(
                f"Ambiguous helper call '{name}' on '{source_type}': matching "
                f"contexts are {', '.join(contexts)}."
            )

        return best_helpers[0]

    @staticmethod
    def _raise_helper_context_error(name: str, helpers: list, source_type: str) -> None:
        contexts = sorted(
            {helper.get("context_type") or "Module" for helper in helpers}
        )
        expected = ", ".join(contexts)

        if source_type == "Module":
            raise SemanticError(
                f"Context helper '{name}' cannot be called through thisModule; "
                f"expected context: {expected}."
            )

        if contexts == ["Module"]:
            raise SemanticError(
                f"Module helper '{name}' must be called through thisModule."
            )

        raise SemanticError(
            f"Helper '{name}' cannot be called on '{source_type}', expected one "
            f"of: {expected}."
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
            if op == '+' and (left_type == "String" or right_type == "String"):
                return "String"
            if left_type == "Unknown" or right_type == "Unknown":
                return "Unknown"
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

        # Iterator expressions (select, reject, collect, forAll, exists,
        # any, ...) are defined only for collections.  Do this check before
        # binding the iterator variable: otherwise a scalar receiver produces
        # an Unknown iterator type and errors such as
        # ``singleReference->reject(...)`` pass Layer 2 unnoticed.
        if (
            is_enabled(ablation_config, "enable_layer2_type_check")
            and source_type != "Unknown"
            and not cls.is_collection_type(source_type)
        ):
            raise SemanticError(
                f"Iterator '{iter_type}' requires a collection source, got {source_type}"
            )

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

            # Like ``select``, ``any`` may narrow its result through a type
            # guard in the predicate.  For example, selecting from
            # ``Collection(XML!Node)`` with
            # ``c.oclIsTypeOf(XML!Attribute) and ...`` yields an
            # ``XML!Attribute``, not merely an ``XML!Node``.
            if len(expr.iterators) == 1:
                refined_type = cls._find_iterator_type_guard(
                    expr.body,
                    expr.iterators[0].name,
                    element_type,
                    env,
                )
                if refined_type is not None:
                    return refined_type

            # ``any`` selects one member satisfying the predicate; it never
            # returns the source collection.
            return cls._single_collection_element_type(source_type)

        raise SemanticError(
            f"Unknown iterator type '{iter_type}'. "
            f"So far only forAll, exists, select, reject, collect, isUnique, sortedBy, any are supported"
        )


    @classmethod
    def _check_collection_op(cls, expr, env, ablation_config=None) -> str:
        source_type = cls.check(expr.source, env, ablation_config=ablation_config)
        op = expr.operation_name

        # ``CollectionOperation`` is rendered as ``receiver->operation(...)``
        # by AST2ATL.  Rejecting scalar receivers here prevents an Ecore
        # reference such as ``self.familySon`` from becoming the invalid
        # ``self->familySon()`` in generated ATL.
        if (
            is_enabled(ablation_config, "enable_layer2_type_check")
            and source_type != "Unknown"
            and not cls.is_collection_type(source_type)
        ):
            raise SemanticError(
                f"Collection operation '{op}' requires a collection source, "
                f"got {source_type}. Use PropertyCall for an Ecore feature."
            )

        if (
            is_enabled(ablation_config, "enable_layer2_existence_check")
            and op not in _COLLECTION_OPERATIONS
        ):
            supported = ", ".join(sorted(_COLLECTION_OPERATIONS))
            raise SemanticError(
                f"Unknown collection operation '{op}'. Supported operations: {supported}. "
                "Use PropertyCall for an Ecore attribute or reference."
            )

        if op == "size": return "Integer"
        if op == "isEmpty": return "Boolean"
        if op == "notEmpty": return "Boolean"
        if op == "sum": return "Integer"
        if op in ("first", "last"):
            return cls._single_collection_element_type(source_type)
        if op == "at":
            if len(expr.arguments) != 1:
                raise SemanticError("at expects exactly one argument")
            index_type = cls.check(expr.arguments[0], env, ablation_config=ablation_config)
            if is_enabled(ablation_config, "enable_layer2_type_check") and index_type not in ("Integer", "Unknown"):
                raise SemanticError(f"at index must be Integer, got {index_type}")
            return cls._single_collection_element_type(source_type)
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

        if not is_enabled(ablation_config, "enable_layer2_type_check"):
            pass
        else:
            if cond_type not in ("Boolean", "Unknown"):
                raise SemanticError(
                    f"If condition should be Boolean but not {cond_type}"
                )

        env.push_scope()
        try:
            cls._apply_guard_type_refinements(expr.condition, env)
            then_type = cls.check(expr.then_expression, env, ablation_config=ablation_config)
        finally:
            env.pop_scope()

        else_type = cls.check(expr.else_expression, env, ablation_config=ablation_config)

        if then_type == else_type:
            return then_type
        if then_type == "Unknown": return else_type
        if else_type == "Unknown": return then_type

        if {then_type, else_type} <= {"Integer", "Real"}:
            return "Real"

        if then_type == "Null":
            return else_type
        if else_type == "Null":
            return then_type

        if cls._is_type_compatible(then_type, else_type, env):
            return else_type
        if cls._is_type_compatible(else_type, then_type, env):
            return then_type

        # Sibling EClasses are also valid branches when they have a common
        # ancestor.  For example, ``ReturnStat`` and ``SelectStat`` both
        # conform to ``Statement`` even though neither conforms to the other.
        common_type = cls._least_common_supertype(then_type, else_type, env)
        if common_type is not None:
            return common_type

        # Unrelated branch types still have the OCL root type as their least
        # common supertype. The surrounding helper/binding can then decide
        # whether OclAny is sufficiently precise for its declared target.
        return "OclAny"

    @classmethod
    def _least_common_supertype(cls, first_type: str, second_type: str, env):
        """Return the unique nearest shared EClass ancestor, if one exists."""
        if env is None or env.registry is None:
            return None

        registry = env.registry
        first_type = registry.resolve_class_name(cls._normalize_type(first_type))
        second_type = registry.resolve_class_name(cls._normalize_type(second_type))

        if (
            first_type not in registry.uml_context
            or second_type not in registry.uml_context
        ):
            return None

        def ancestor_distances(type_name: str) -> dict[str, int]:
            distances = {}
            queue = [(type_name, 0)]

            while queue:
                current_type, distance = queue.pop(0)
                if current_type in distances:
                    continue

                distances[current_type] = distance
                class_info = registry.uml_context.get(current_type, {})
                for super_type in class_info.get("super_classes", []):
                    queue.append((super_type, distance + 1))

            return distances

        first_ancestors = ancestor_distances(first_type)
        second_ancestors = ancestor_distances(second_type)
        shared = set(first_ancestors) & set(second_ancestors)
        if not shared:
            return None

        # Prefer the closest common ancestor.  If multiple inheritance leaves
        # several incomparable nearest ancestors, retain the mismatch rather
        # than selecting an arbitrary type.
        ranked = sorted(
            shared,
            key=lambda type_name: (
                max(first_ancestors[type_name], second_ancestors[type_name]),
                first_ancestors[type_name] + second_ancestors[type_name],
                type_name,
            ),
        )
        best = ranked[0]
        best_rank = (
            max(first_ancestors[best], second_ancestors[best]),
            first_ancestors[best] + second_ancestors[best],
        )
        if sum(
            (
                max(first_ancestors[type_name], second_ancestors[type_name]),
                first_ancestors[type_name] + second_ancestors[type_name],
            )
            == best_rank
            for type_name in ranked
        ) > 1:
            return None

        return best


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
    def _single_collection_element_type(cls, source_type: str) -> str:
        """Return the scalar element type selected by ``any``/``first``/``last``/``at``.

        Registry property types may carry a cardinality suffix (for example
        ``KM3!Reference[0..1]``). A collection selector yields the element,
        not that element's multiplicity annotation, so normalize it here
        before the binding compatibility check.
        """
        return cls._normalize_type(cls._element_type(source_type))

    @classmethod
    def _select_refined_collection_type(cls, expr, source_type: str, element_type: str, env) -> str:
        match = re.match(r'^(Set|Bag|Sequence|OrderedSet)\(([^)]+)\)$', source_type)
        if not match or len(expr.iterators) != 1:
            return None

        iterator_name = expr.iterators[0].name
        refined_type = cls._find_iterator_type_guard(
            expr.body,
            iterator_name,
            element_type,
            env,
        )
        if refined_type is None:
            return None

        return f"{match.group(1)}({refined_type})"

    @classmethod
    def _find_iterator_type_guard(
        cls,
        expression,
        iterator_name: str,
        element_type: str,
        env,
    ):
        """Find a safe iterator type guard in an iterator predicate.

        A conjunction such as ``c.oclIsKindOf(XML!Element) and c.name = name``
        still narrows the selected collection to ``XML!Element``.  Do not
        recurse through ``or``: either branch may be true without satisfying
        the type guard, so narrowing would be unsound.
        """
        if (
            expression.type == "OperationCall"
            and expression.operation_name in ("oclIsKindOf", "oclIsTypeOf")
            and expression.source.type == "Variable"
            and expression.source.name == iterator_name
            and len(expression.arguments) == 1
        ):
            target = expression.arguments[0]
            if target.type != "Variable" or "!" not in target.name:
                return None
            if (
                element_type != "Unknown"
                and not cls._is_type_compatible(target.name, element_type, env)
            ):
                return None
            return target.name

        if expression.type != "BinaryExpression" or expression.operator != "and":
            return None

        left_type = cls._find_iterator_type_guard(
            expression.left,
            iterator_name,
            element_type,
            env,
        )
        right_type = cls._find_iterator_type_guard(
            expression.right,
            iterator_name,
            element_type,
            env,
        )

        if left_type is None:
            return right_type
        if right_type is None:
            return left_type

        # When both sides constrain the same iterator, retain the more
        # specific compatible type. Unrelated guards do not justify a safe
        # static narrowing.
        if cls._is_type_compatible(left_type, right_type, env):
            return left_type
        if cls._is_type_compatible(right_type, left_type, env):
            return right_type
        return None

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

        # Unknown is a wildcard used when a type cannot be inferred yet,
        # including the element type of an empty collection literal.
        if actual_type == "Unknown" or expected_type == "Unknown":
            return True

        # OclAny is the root OCL type. Compatibility is intentionally
        # directional: concrete -> OclAny is valid, OclAny -> concrete is not.
        if expected_type == "OclAny":
            return True

        # Primitive compatibility
        if expected_type in cls._compatible_types(actual_type):
            return True

        # Collection compatibility
        # A bare collection type is the legacy representation of a
        # collection whose element type could not be inferred.  Treat it as
        # ``Kind(Unknown)`` so, for example, ``Set`` and ``Set(Unknown)``
        # unify, while different collection kinds remain incompatible.
        src_match = re.fullmatch(
            r'(Set|Bag|Sequence|OrderedSet)(?:\((.+)\))?',
            actual_type
        )
        tgt_match = re.fullmatch(
            r'(Set|Bag|Sequence|OrderedSet)(?:\((.+)\))?',
            expected_type
        )

        if src_match and tgt_match:
            src_collection = src_match.group(1)
            tgt_collection = tgt_match.group(1)

            if src_collection != tgt_collection:
                return False

            return cls._is_type_compatible(
                src_match.group(2) or "Unknown",
                tgt_match.group(2) or "Unknown",
                env
            )

        # Một bên collection, một bên không
        if src_match or tgt_match:
            return False

        # EClass inheritance
        if env and env.registry:
            actual_type = env.registry.resolve_class_name(actual_type)
            expected_type = env.registry.resolve_class_name(expected_type)

            src_base = actual_type.split("!")[-1]
            tgt_base = expected_type.split("!")[-1]

            queue = [actual_type]
            visited = set()

            while queue:
                current_class = queue.pop(0)
                if current_class in visited:
                    continue
                visited.add(current_class)

                if (
                    current_class == expected_type
                    or current_class.split("!")[-1] == tgt_base
                ):
                    return True

                class_info = env.registry.uml_context.get(current_class)

                if not class_info:
                    continue

                for super_cls in class_info.get("super_classes", []):
                    queue.append(super_cls)

        return False

    @staticmethod
    def _normalize_type(type_name: str) -> str:
        if type_name is None:
            return type_name
        return re.sub(r'\[[^\]]+\]$', '', type_name).strip()
