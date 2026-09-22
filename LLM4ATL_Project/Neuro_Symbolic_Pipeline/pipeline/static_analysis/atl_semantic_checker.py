import re
from common.atl_identifiers import atl_identifier_error
from config.ablation_config import is_enabled
from pipeline.structural_checking.schema.atl_ast import *
from .type_environment import TypeEnvironment
from .ocl_semantic_checker import OCLSemanticChecker
from .errors import SemanticError

class ATLSemanticChecker:
    _BARE_COLLECTION_TYPE = re.compile(r"^(Set|Bag|Sequence|OrderedSet)$")

    @classmethod
    def check(cls, document:ATLDocument, env:TypeEnvironment, ablation_config=None):
        module = document.module

        return cls.check_module(module, env, ablation_config)

    @classmethod
    def check_module(cls, module:Module, env:TypeEnvironment, ablation_config=None):
        if not is_enabled(ablation_config, "enable_layer2_semantic"):
            return

        # Kiểm tra tên module
        if not module.name:
            raise SemanticError("Module name is missing.")
        identifier_error = atl_identifier_error(module.name)
        if identifier_error is not None:
            raise SemanticError(
                f"Invalid ATL module name '{module.name}': {identifier_error}."
            )

        # Kiểm tra input models
        for model in module.input_models:
          cls._check_model_declaration(model, env)

        # Kiểm tra output models
        for model in module.output_models:
          cls._check_model_declaration(model, env)

        # Đăng ký các Helper
        for element in module.elements:
            if isinstance(element, Helper):
                cls._register_helper(element, env)

        # Đăng ký các Rule
        for element in module.elements:
            if isinstance(element, (MatchedRule, LazyMatchedRule, CalledRule)):
                cls._register_rule(element, env)

        # Kiểm tra các thành phần khác của module 
        for element in module.elements:

            if isinstance(element, LazyMatchedRule):
                cls._check_lazy_matched_rule(element, env, ablation_config)

            elif isinstance(element, MatchedRule):
                cls._check_matched_rule(element, env, ablation_config)

            elif isinstance(element, CalledRule):
                cls._check_called_rule(element, env, ablation_config)

            elif isinstance(element, Helper):
                cls._check_helper(element, env, ablation_config)

            else:
                raise SemanticError(f"Unknown module element type: {type(element)}")

    @classmethod
    def _check_model_declaration(cls, model:ModelDeclaration, env:TypeEnvironment):
        if not model.alias:
            raise SemanticError("Model alias is missing.")
        if not model.metamodel:
            raise SemanticError("Model metamodel is missing.")
        if model.alias in env.scopes[0]:
            raise SemanticError(f"Duplicate model alias: {model.alias}")

        env.bind_variable(model.alias, model.metamodel)

    @classmethod
    def _register_helper(cls, helper:Helper, env:TypeEnvironment):
        if not helper.name:
            raise SemanticError("Helper name is missing.")
        if not helper.return_type or not str(helper.return_type).strip():
            raise SemanticError(f"Helper '{helper.name}' is missing return type.")
        cls._validate_emittable_type(
            helper.return_type,
            f"Helper '{helper.name}' return type",
        )

        for param in helper.parameters:
            if param.declared_type:
                cls._validate_emittable_type(
                    param.declared_type,
                    f"Helper '{helper.name}' parameter '{param.name}' type",
                )

        env.register_helper(
            name=helper.name,
            parameter_types=[
                param.declared_type
                for param in helper.parameters
            ],
            return_type=helper.return_type,
            context_type=helper.context_type,
            kind=helper.kind
        )

    @classmethod
    def _validate_emittable_type(cls, type_name: str, label: str) -> None:
        """Reject type annotations that AST2ATL cannot render as valid ATL.

        A bare collection name is useful internally as an inferred
        ``Kind(Unknown)`` type, but is not legal in an ATL declaration.  The
        AST generator emits declared types verbatim, so declarations must
        carry their element type.
        """
        normalized = str(type_name).strip()
        match = cls._BARE_COLLECTION_TYPE.fullmatch(normalized)
        if match:
            kind = match.group(1)
            raise SemanticError(
                f"{label} cannot be bare '{kind}'. "
                f"Use '{kind}(ElementType)'."
            )

    @classmethod
    def _check_helper(cls, helper:Helper, env:TypeEnvironment, ablation_config=None):

        env.push_scope()

        try: 
            if helper.context_type is not None:
                env.bind_variable("self", helper.context_type, allow_builtin=True)

            for param in helper.parameters:
                env.bind_variable(param.name, param.declared_type)

            body_type = OCLSemanticChecker.check(helper.body, env, ablation_config)

            if (
                is_enabled(ablation_config, "enable_layer2_type_check")
                and helper.return_type is not None
                and body_type != "Unknown"
                and not cls._is_compatible_type(body_type, helper.return_type, env)
            ):
                raise SemanticError(f"Helper '{helper.name}' return type mismatch: expected {helper.return_type}, got {body_type}")

        finally:
            env.pop_scope()

    @classmethod
    def _register_rule(cls, rule:Rule, env:TypeEnvironment):
        if not rule.name:
            raise SemanticError("Rule name is missing.")

        if isinstance(rule, CalledRule):

            parameter_types = [
                param.declared_type
                for param in rule.parameters
            ]

        elif isinstance(rule, (MatchedRule, LazyMatchedRule)):
            parameter_types = []
            for element in rule.in_pattern.elements:
                variable = element.variable
                if not variable.declared_type or not str(variable.declared_type).strip():
                    raise SemanticError(f"InPattern variable '{variable.name}' is missing declared type.")
                parameter_types.append(str(variable.declared_type).strip())

        else:
            raise SemanticError(f"Unknown rule type: {type(rule)}")

        output_types = []
        output_variables = {}

        if rule.out_pattern is not None:
            for element in rule.out_pattern.elements:
                variable = element.variable
                if not variable.declared_type or not str(variable.declared_type).strip():
                    raise SemanticError(f"OutPattern variable '{variable.name}' is missing declared type.")
                declared_type = str(variable.declared_type).strip()
                output_types.append(declared_type)
                output_variables[variable.name] = declared_type

        env.register_rule(
            name=rule.name,
            parameter_types=parameter_types,
            output_types=output_types,
            rule_kind=rule.type,
            output_variables=output_variables,
        )

    @classmethod
    def _check_matched_rule(cls, rule:MatchedRule, env:TypeEnvironment, ablation_config=None):
        env.push_scope()

        try:
            cls._check_in_pattern(rule.in_pattern, env, ablation_config)

            cls._check_using(rule.using, env, ablation_config)

            if rule.out_pattern is not None:
                cls._check_out_pattern(rule.out_pattern, env, ablation_config)

            if rule.action_block is not None:
                cls._check_action_block(rule.action_block, env, ablation_config)

        finally:
            env.pop_scope()

    @classmethod
    def _check_in_pattern(cls, in_pattern:InPattern, env:TypeEnvironment, ablation_config=None):
        for element in in_pattern.elements:
            variable = element.variable
            if not variable.declared_type or not str(variable.declared_type).strip():
                raise SemanticError(f"InPattern variable '{variable.name}' is missing declared type.")

            declared_type = cls._validate_pattern_type(
                variable.name,
                variable.declared_type,
                "InPattern",
                env,
                ablation_config,
            )
            env.bind_variable(variable.name, declared_type)

        if in_pattern.filter is not None:

            filter_type = OCLSemanticChecker.check(in_pattern.filter, env, ablation_config)

            if is_enabled(ablation_config, "enable_layer2_type_check") and filter_type not in ["Boolean", "Unknown"]:
                raise SemanticError(f"InPattern filter must be Boolean, got {filter_type}")

            cls._apply_filter_type_refinements(in_pattern.filter, env)

    @classmethod
    def _apply_filter_type_refinements(cls, expr, env:TypeEnvironment):
        if expr is None:
            return

        if expr.type == "BinaryExpression" and expr.operator == "and":
            cls._apply_filter_type_refinements(expr.left, env)
            cls._apply_filter_type_refinements(expr.right, env)
            return

        if expr.type == "OperationCall" and expr.operation_name in ("oclIsKindOf", "oclIsTypeOf"):
            if len(expr.arguments) != 1:
                return

            source = expr.source
            target = expr.arguments[0]
            if source.type == "Variable" and target.type == "Variable" and "!" in target.name:
                # This updates the inferred type of an existing variable; it
                # is not a user declaration. Built-ins such as ``self`` may
                # therefore be refined by an oclIsKindOf/oclIsTypeOf guard.
                env.bind_variable(source.name, target.name, allow_builtin=True)

    @classmethod
    def _check_using(cls, declarations, env:TypeEnvironment, ablation_config=None):
        for decl in declarations:
            value_type = OCLSemanticChecker.check(decl.init_expression, env, ablation_config)


            declared_type = decl.variable.declared_type

            if (
                is_enabled(ablation_config, "enable_layer2_type_check")
                and declared_type is not None
                and value_type != "Unknown"
                and not cls._is_compatible_type(value_type, declared_type, env)
            ):
                raise SemanticError(f"Using declaration '{decl.variable.name}' type mismatch: expected {declared_type}, got {value_type}")

            env.bind_variable(decl.variable.name,  declared_type or value_type)

    @classmethod
    def _check_out_pattern(cls, out_pattern:OutPattern, env:TypeEnvironment, ablation_config=None):
        for element in out_pattern.elements:
            variable = element.variable
            if not variable.declared_type or not str(variable.declared_type).strip():
                raise SemanticError(f"OutPattern variable '{variable.name}' is missing declared type.")

            declared_type = cls._validate_pattern_type(
                variable.name,
                variable.declared_type,
                "OutPattern",
                env,
                ablation_config,
            )
            env.bind_variable(variable.name, declared_type)

        for element in out_pattern.elements:
            variable = element.variable
            target_type = str(variable.declared_type).strip()

            cls._check_bindings(element.bindings, target_type, env, ablation_config)

    @classmethod
    def _validate_pattern_type(
        cls,
        variable_name,
        declared_type,
        pattern_kind,
        env:TypeEnvironment,
        ablation_config=None,
    ) -> str:
        declared_type = str(declared_type).strip()
        if not is_enabled(ablation_config, "enable_layer2_existence_check"):
            return declared_type

        if env.registry is None:
            raise SemanticError("Registry is not set in the type environment.")

        resolved_type = env.registry.resolve_class_name(declared_type)
        if resolved_type not in env.registry.uml_context:
            raise SemanticError(
                f"{pattern_kind} variable '{variable_name}' has unknown declared "
                f"type '{declared_type}'. Use an Ecore metamodel-qualified type "
                "instead of a model alias such as 'IN' or 'OUT'."
            )

        return resolved_type

    @classmethod
    def _check_bindings(cls, bindings, target_type:str, env:TypeEnvironment, ablation_config=None):
        for binding in bindings:
            value_type = OCLSemanticChecker.check(binding.value, env, ablation_config)

            if env.registry is None:
                if is_enabled(ablation_config, "enable_layer2_existence_check"):
                    raise SemanticError(
                        "Registry is not set in the type environment."
                    )
                property_type = "Unknown"
            else:
                try:
                    property_type = env.registry.resolve_property(target_type, binding.property_name)
                except SemanticError:
                    if is_enabled(ablation_config, "enable_layer2_existence_check"):
                        raise
                    property_type = "Unknown"

            if (
                is_enabled(ablation_config, "enable_layer2_type_check")
                and value_type != "Unknown"
                and property_type != "Unknown"
                and not cls._is_compatible_type(value_type, property_type, env)
            ):
                display_property_type = cls._normalize_type(property_type)
                raise SemanticError(
                    f"Binding for property '{binding.property_name}' type mismatch: "
                    f"expected {display_property_type}, got {value_type}"
                )

    @classmethod
    def _is_compatible_type(cls, source_type:str, target_type:str, env:TypeEnvironment=None) -> bool:
        source_type = cls._normalize_type(source_type)
        target_type = cls._normalize_type(target_type)

        if source_type == target_type:
            return True
        if source_type == "Unknown" or target_type == "Unknown":
            return True
        # OclAny is the root OCL type. Every concrete value conforms to it,
        # but an OclAny value does not conform to an arbitrary concrete type.
        if target_type == "OclAny":
            return True
        if source_type == "Null":
            return True

        if source_type == "Integer" and target_type == "Real":
            return True

        import re
        # A bare collection type is the legacy representation of a
        # collection whose element type could not be inferred. Treat it as
        # ``Kind(Unknown)`` so ``Set`` and ``Set(Unknown)`` are compatible,
        # just like the OCL expression checker.
        src_match = re.fullmatch(
            r'(Set|Bag|Sequence|OrderedSet)(?:\((.+)\))?', source_type
        )
        tgt_match = re.fullmatch(
            r'(Set|Bag|Sequence|OrderedSet)(?:\((.+)\))?', target_type
        )

        # Cả hai đều là collection
        if src_match and tgt_match:
            # Preserve ATL's existing collection coercion behavior. Missing
            # element types are treated as Unknown during unification, so
            # ``Set`` and ``Set(Unknown)`` are compatible.
            return cls._is_compatible_type(
                src_match.group(2) or "Unknown",
                tgt_match.group(2) or "Unknown",
                env,
            )
        
        # Nếu source là collection nhưng target không phải
        if src_match and not tgt_match:
            return False
        
        if source_type in ("Set", "Bag", "Sequence", "OrderedSet") and tgt_match:
            return True

        if tgt_match and not src_match:
            # Preserve the existing ATL implicit element-to-collection
            # compatibility rule.
            return cls._is_compatible_type(
                source_type, tgt_match.group(2) or "Unknown", env
            )

        # Kiểm tra tính kế thừa UML
        if env and env.registry:
            source_type = env.registry.resolve_class_name(source_type)
            target_type = env.registry.resolve_class_name(target_type)

            if "!" in source_type and "!" in target_type:
                if source_type.split("!")[0] != target_type.split("!")[0]:
                    # Cho phép Implicit Trace Resolution của ATL khi gán phần tử nguồn vào thuộc tính đích
                    return True
            
            src_base = source_type.split("!")[-1]
            tgt_base = target_type.split("!")[-1]
            current_class = source_type

            queue = [current_class]
            visited = set()
            
            while queue:
                curr = queue.pop(0)
                if curr in visited:
                    continue
                visited.add(curr)
                
                if curr == target_type or curr.split("!")[-1] == tgt_base:
                    return True
                    
                if curr in env.registry.uml_context:
                    for super_cls in env.registry.uml_context[curr].get("super_classes", []):
                        queue.append(super_cls)

        return False

    @staticmethod
    def _normalize_type(type_name: str) -> str:
        if type_name is None:
            return type_name
        return re.sub(r'\[[^\]]+\]$', '', type_name).strip()

    @classmethod
    def _check_action_block(cls, action_block:ActionBlock, env:TypeEnvironment, ablation_config=None):
        for statement in action_block.statements:
            cls._check_statement(statement, env, ablation_config)

    @classmethod
    def _check_statement(cls, statement:Statement, env:TypeEnvironment, ablation_config=None):
        if isinstance(statement, ExpressionStatement):
            OCLSemanticChecker.check(statement.expression, env, ablation_config)

        elif isinstance(statement, BindingStatement):
            value_type = OCLSemanticChecker.check(statement.value, env, ablation_config)

            target_type = OCLSemanticChecker.check(statement.target, env, ablation_config)

            if (
                is_enabled(ablation_config, "enable_layer2_type_check")
                and value_type != "Unknown"
                and target_type != "Unknown"
                and not cls._is_compatible_type(value_type, target_type, env)
            ):
                raise SemanticError(f"Binding statement type mismatch: expected {target_type}, got {value_type}")

        elif isinstance(statement, IfStatement):
            condition_type = OCLSemanticChecker.check(statement.condition, env, ablation_config)

            if is_enabled(ablation_config, "enable_layer2_type_check") and condition_type != "Boolean" and condition_type != "Unknown":
                raise SemanticError(f"If statement condition must be Boolean, got {condition_type}")

            env.push_scope()
            try:
                for stmt in statement.then_statements:
                    cls._check_statement(stmt, env, ablation_config)
            finally:
                env.pop_scope()

            env.push_scope()
            try:
                for stmt in statement.else_statements:
                    cls._check_statement(stmt, env, ablation_config)
            finally:
                env.pop_scope()

        elif isinstance(statement, ForStatement):
            collection_type = OCLSemanticChecker.check(statement.collection, env, ablation_config)

            element_type = OCLSemanticChecker._element_type(collection_type)  

            env.push_scope()
            try:
                env.bind_variable(statement.iterator.name, element_type)

                for stmt in statement.body:
                    cls._check_statement(stmt, env, ablation_config)
            finally:
                env.pop_scope()

        else:
            raise SemanticError(f"Unknown statement type: {type(statement)}")

    @classmethod
    def _check_lazy_matched_rule(cls, rule:LazyMatchedRule, env:TypeEnvironment, ablation_config=None):
        cls._check_matched_rule(rule, env, ablation_config)

        # if not isinstance(rule.is_unique, bool):
        #     raise SemanticError(f"LazyMatchedRule 'is_unique' must be a boolean, got {type(rule.is_unique)}")

    @classmethod
    def _check_called_rule(cls, rule:CalledRule, env:TypeEnvironment, ablation_config=None):

        env.push_scope()
        try:
            seen = set()

            for param in rule.parameters:
                if param.name in seen:
                    raise SemanticError(f"Duplicate parameter name: {param.name}")

                seen.add(param.name)

                if not param.declared_type:
                    raise SemanticError(f"Parameter '{param.name}' is missing declared type.")
                
                env.bind_variable(param.name, param.declared_type)

            cls._check_using(rule.using, env, ablation_config)

            if rule.out_pattern is not None:
                cls._check_out_pattern(rule.out_pattern, env, ablation_config)

            if rule.action_block is not None:
                cls._check_action_block(rule.action_block, env, ablation_config)

        finally:
            env.pop_scope()

