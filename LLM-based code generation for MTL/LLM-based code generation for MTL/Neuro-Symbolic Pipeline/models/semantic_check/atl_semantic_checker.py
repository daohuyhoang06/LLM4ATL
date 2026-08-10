from schema.atl_ast import *
from .type_environment import TypeEnvironment
from .ocl_semantic_checker import OCLSemanticChecker
from .errors import SemanticError

class ATLSemanticChecker:
    @classmethod
    def check(cls, document:ATLDocument, env:TypeEnvironment, ablation_config=None):
        module = document.module

        return cls.check_module(module, env, ablation_config)

    @classmethod
    def check_module(cls, module:Module, env:TypeEnvironment, ablation_config=None):

        # Kiểm tra tên module
        if not module.name:
            raise SemanticError("Module name is missing.")

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
    def _check_helper(cls, helper:Helper, env:TypeEnvironment, ablation_config=None):

        env.push_scope()

        try: 
            if helper.context_type is not None:
                env.bind_variable("self", helper.context_type)

            for param in helper.parameters:
                env.bind_variable(param.name, param.declared_type)

            body_type = OCLSemanticChecker.check(helper.body, env, ablation_config)

            if helper.return_type is not None and body_type != "Unknown" and body_type != helper.return_type:
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
            parameter_types = [
                element.variable.declared_type
                for element in rule.in_pattern.elements
            ]

        else:
            raise SemanticError(f"Unknown rule type: {type(rule)}")

        output_types = []

        if rule.out_pattern is not None:
            for element in rule.out_pattern.elements:
                output_types.append(element.variable.declared_type)

        env.register_rule(
            name=rule.name,
            parameter_types=parameter_types,
            output_types=output_types,
            rule_kind=rule.type
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

            env.bind_variable(variable.name, variable.declared_type)

        if in_pattern.filter is not None:

            filter_type = OCLSemanticChecker.check(in_pattern.filter, env, ablation_config)

            if filter_type not in ["Boolean", "Unknown"]:
                raise SemanticError(f"InPattern filter must be Boolean, got {filter_type}")

    @classmethod
    def _check_using(cls, declarations, env:TypeEnvironment, ablation_config=None):
        for decl in declarations:
            value_type = OCLSemanticChecker.check(decl.init_expression, env, ablation_config)


            declared_type = decl.variable.declared_type

            if declared_type is not None and value_type != "Unknown" and not cls._is_compatible_type(value_type, declared_type):
                raise SemanticError(f"Using declaration '{decl.variable.name}' type mismatch: expected {declared_type}, got {value_type}")

            env.bind_variable(decl.variable.name,  declared_type or value_type)

    @classmethod
    def _check_out_pattern(cls, out_pattern:OutPattern, env:TypeEnvironment, ablation_config=None):
        for element in out_pattern.elements:
            variable = element.variable

            env.bind_variable(variable.name, variable.declared_type)

            cls._check_bindings(element.bindings, variable.declared_type, env, ablation_config)

    @classmethod
    def _check_bindings(cls, bindings, target_type:str, env:TypeEnvironment, ablation_config=None):
        for binding in bindings:
            value_type = OCLSemanticChecker.check(binding.value, env, ablation_config)

            property_type = env.registry.resolve_property(target_type, binding.property_name)

            if value_type != "Unknown" and property_type != "Unknown" and not cls._is_compatible_type(value_type, property_type):
                raise SemanticError(f"Binding for property '{binding.property_name}' type mismatch: expected {property_type}, got {value_type}")

    @classmethod
    def _is_compatible_type(cls, source_type:str, target_type:str) -> bool:
        if source_type == target_type:
            return True

        # Kiểm tra các trường hợp đặc biệt
        if source_type == "Integer" and target_type == "Real":
            return True

        return False

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

            if value_type != "Unknown" and target_type != "Unknown" and not cls._is_compatible_type(value_type, target_type):
                raise SemanticError(f"Binding statement type mismatch: expected {target_type}, got {value_type}")

        elif isinstance(statement, IfStatement):
            condition_type = OCLSemanticChecker.check(statement.condition, env, ablation_config)

            if condition_type != "Boolean" and condition_type != "Unknown":
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

