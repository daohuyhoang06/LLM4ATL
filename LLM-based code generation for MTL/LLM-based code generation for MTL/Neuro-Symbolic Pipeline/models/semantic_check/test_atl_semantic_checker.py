from schema.atl_ast import ModelDeclaration, Helper, MatchedRule, LazyMatchedRule, InPattern, InPatternElement, OutPattern, OutPatternElement, RuleVariableDeclaration, Binding, ExpressionStatement, BindingStatement, IfStatement, ForStatement, ActionBlock, StatementNode, ModuleElementNode, Module, Variable, TypeLiteral, SimpleOutPatternElement, ForEachOutPatternElement
from schema.ocl_ast import LiteralExpression, Variable, OperationCall, PropertyCall
from semantic_check.atl_semantic_checker import ATLSemanticChecker
from semantic_check.type_environment import TypeEnvironment
from semantic_check.errors import SemanticError
from semantic_check.ocl_semantic_checker import OCLSemanticChecker

class MockRegistry:
    def __init__(self):
        self.properties = {
            "Grafcet!Grafcet": {
                "name": "String",
                "states": "Set(State)"
            },
            "ascet!SoftwareGrafcet": {
                "name": "String"
            }
        }

    def resolve_property(self, type_name, property_name):
        return self.properties.get(
            type_name,
            {}
        ).get(
            property_name,
            "Unknown"
        )

def test_matched_rule_basic():
    env = TypeEnvironment()

    registry = MockRegistry()
    env.registry = registry

    rule = MatchedRule(
        name="Register2Register",

        in_pattern=InPattern(
            elements=[
                InPatternElement(
                    variable=Variable(
                        name="fr",
                        declared_type="family!FamilyRegister"
                    )
                )
            ]
        ),

        out_pattern=OutPattern(
            elements=[
                SimpleOutPatternElement(
                    type="SimpleOutPatternElement",
                    variable=Variable(
                        name="pr",
                        declared_type="person!PersonRegister"
                    ),
                    bindings=[]
                )
            ]
        )
    )

    ATLSemanticChecker._check_matched_rule(
        rule,
        env
    )

    print("MatchedRule basic: PASS")

def test_called_rule_wrong_argument_count():
    env = TypeEnvironment()

    env.register_rule(
        name="CreateSoftwareTask",
        parameter_types=["amalthea!Task"],
        output_types=["ascet!SoftwareTask"],
        rule_kind="CalledRule"
    )

    expr = OperationCall(
        source=Variable(
            name="thisModule",
            declared_type="Module"
        ),
        operation_name="CreateSoftwareTask",
        arguments=[]
    )

    try:
        OCLSemanticChecker.check(expr, env)

        assert False, "Expected SemanticError"

    except SemanticError as e:
        print("CalledRule wrong argument count: PASS")
        print("Caught:", e)

if __name__ == "__main__":
    test_called_rule_wrong_argument_count()
    print("Test passed: test_called_rule_wrong_argument_count")