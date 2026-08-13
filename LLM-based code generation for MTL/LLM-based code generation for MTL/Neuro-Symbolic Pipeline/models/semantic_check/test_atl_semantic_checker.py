from schema.atl_ast import ModelDeclaration, Helper, MatchedRule, LazyMatchedRule, InPattern, InPatternElement, OutPattern, OutPatternElement, RuleVariableDeclaration, Binding, ExpressionStatement, BindingStatement, IfStatement, ForStatement, ActionBlock, StatementNode, ModuleElementNode, Module, Variable, TypeLiteral, SimpleOutPatternElement, ForEachOutPatternElement
from schema.ocl_ast import LiteralExpression, Variable, OperationCall, PropertyCall
from semantic_check.atl_semantic_checker import ATLSemanticChecker
from semantic_check.type_environment import TypeEnvironment
from semantic_check.errors import SemanticError
from semantic_check.ocl_semantic_checker import OCLSemanticChecker

from semantic_check.ecore_registry import ATLEcoreRegistry
import os
import json

def get_uml_context():
    ecore_path = r"D:\LLM4MTLs goc\LLM-based code generation for MTL\LLM-based code generation for MTL\Neuro-Symbolic Pipeline\models\ATL_model\Families.ecore"

    registry = ATLEcoreRegistry([ecore_path])

    env = TypeEnvironment()
    env.registry = registry

    print("UML CONTEXT:")
    print(json.dumps(
        registry.uml_context,
        indent=4,
        ensure_ascii=False
    ))

def test_component_container_properties():

    ecore_path = r"D:\LLM4MTLs goc\LLM-based code generation for MTL\LLM-based code generation for MTL\Neuro-Symbolic Pipeline\models\ATL_model\amalthea.ecore"

    registry = ATLEcoreRegistry([ecore_path])

    print("\n=== ALL UML CONTEXT ===")

    for class_name, info in registry.uml_context.items():
        print(class_name)

    print("\n=== ComponentContainer ===")

    print(
        registry.uml_context.get(
            "ComponentContainer"
        )
    )

    actual = registry.resolve_property(
        "amalthea!ComponentContainer",
        "tasks"
    )

    print("\ntasks =", actual)

    assert actual != "Unknown"

    print("PASS: ComponentContainer.tasks")


def test_class_name_property():
    ecore_path = r"D:\LLM4MTLs goc\LLM-based code generation for MTL\LLM-based code generation for MTL\Neuro-Symbolic Pipeline\models\ATL_model\Class.ecore"

    registry = ATLEcoreRegistry([ecore_path])

    print("\n=== Class ===")

    print(registry.uml_context.get("Class"))

    actual = registry.resolve_property(
        "Class!Class",
        "name"
    )

    print("Class.name =", actual)

    assert actual == "String"

    print("PASS: Class.name")


if __name__ == "__main__":
    get_uml_context()