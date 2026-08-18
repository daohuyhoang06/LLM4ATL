from schema.ocl_ast import (
    LiteralExpression,
    Variable,
    BinaryExpression,
    UnaryExpression,
    PropertyCall,
    OperationCall,
    IfExpression,
)
from semantic_check.ocl_semantic_checker import OCLSemanticChecker
from semantic_check.type_environment import TypeEnvironment
from semantic_check.errors import SemanticError

def test_rule_call():
    env = TypeEnvironment()

    env.register_rule(
        name="Task2SoftwareTask",
        parameter_types=["amalthea!Task"],
        output_types=["ascet!SoftwareTask"],
        rule_kind="LazyMatchedRule"
    )

    env.bind_variable("x", "amalthea!Task")

    expr = OperationCall(
        source=Variable(name="thisModule"),
        operation_name="Task2SoftwareTask",
        arguments=[
            Variable(name="x")
        ]
    )

    actual = OCLSemanticChecker.check(expr, env)

    print(
        f"thisModule.Task2SoftwareTask(x): "
        f"expected=ascet!SoftwareTask, actual={actual}"
    )

    assert actual == "ascet!SoftwareTask"

if __name__ == "__main__":
    test_rule_call()
    print("Test passed: test_rule_call")