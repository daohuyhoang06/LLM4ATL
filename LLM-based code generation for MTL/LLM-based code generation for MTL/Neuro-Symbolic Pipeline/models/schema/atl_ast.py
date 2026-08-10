from pydantic import BaseModel, Field
from typing import List, Optional, Union, Annotated
from typing import Literal as TypeLiteral 

from ocl_ast import (
    OCLExpression,
    Variable
)

class ATLNode(BaseModel):

    type: str

class Module(ATLNode):

    type: TypeLiteral["Module"] = "Module"
    name: str
    input_models: List["ModelDeclaration"] = Field(default_factory=list)
    output_models: List["ModelDeclaration"] = Field(default_factory=list)
    elements: List["ModuleElementNode"] = Field(default_factory=list)

class ModelDeclaration(ATLNode):

    type: TypeLiteral["ModelDeclaration"] = "ModelDeclaration"
    alias: str  
    metamodel: str  

class ModuleElement(ATLNode):
    pass

class Parameter(Variable):

    type: TypeLiteral["Parameter"] = "Parameter"

class Helper(ModuleElement):

    type: TypeLiteral["Helper"] = "Helper"
    kind: TypeLiteral["attribute","operation"]
    context_type: Optional[str] = None
    name: str
    parameters: List[Parameter] = Field(default_factory=list)
    return_type: Optional[str] = None
    body: OCLExpression

class Rule(ModuleElement):

    # type: TypeLiteral["Rule"] = "Rule"
    name: str
    using: List["RuleVariableDeclaration"] = Field(default_factory=list)
    out_pattern: Optional["OutPattern"] = None
    action_block: Optional["ActionBlock"] = None

class MatchedRule(Rule):

    type: TypeLiteral["MatchedRule"] = "MatchedRule"
    in_pattern: "InPattern"
    extends: Optional[str] = None
    is_abstract: bool = False
    is_nodefault: bool = False
    is_refining: bool = False

class LazyMatchedRule(MatchedRule):

    type: TypeLiteral["LazyMatchedRule"] = "LazyMatchedRule"
    is_unique: bool = False

class CalledRule(Rule):

    type: TypeLiteral["CalledRule"] = "CalledRule"
    parameters: List[Parameter] = Field(default_factory=list)
    is_entrypoint: bool = False
    is_endpoint: bool = False

class InPattern(ATLNode):

    type: TypeLiteral["InPattern"] = "InPattern"
    elements: List["InPatternElement"] = Field(default_factory=list)
    filter: Optional[OCLExpression] = None

class InPatternElement(ATLNode):

    type: TypeLiteral["InPatternElement"] = "InPatternElement"
    variable: Variable
    model: Optional[str] = None

class OutPattern(ATLNode):

    type: TypeLiteral["OutPattern"] = "OutPattern"
    elements: List["OutPatternElementNode"]

class OutPatternElement(ATLNode):

    # type: TypeLiteral["OutPatternElement"] = "OutPatternElement"
    variable: Variable
    bindings: List["Binding"] = Field(default_factory=list)
    maps_to: Optional[str] = None
    model: Optional[str] = None

class SimpleOutPatternElement(OutPatternElement):

    type: TypeLiteral["SimpleOutPatternElement"] = "SimpleOutPatternElement"

class ForEachOutPatternElement(OutPatternElement):

    type: TypeLiteral["ForEachOutPatternElement"] = "ForEachOutPatternElement"
    iterator: Variable
    collection: OCLExpression
    distinct: bool = True

class Binding(ATLNode):

    type: TypeLiteral["Binding"] = "Binding"
    property_name: str
    value: OCLExpression

class RuleVariableDeclaration(ATLNode):

    type: TypeLiteral["RuleVariableDeclaration"] = "RuleVariableDeclaration"
    variable: Variable       
    init_expression: OCLExpression

class ActionBlock(ATLNode):

    type: TypeLiteral["ActionBlock"] = "ActionBlock"
    statements: List["StatementNode"] = Field(default_factory=list)

class Statement(ATLNode):
    pass

class ExpressionStatement(Statement):

    type: TypeLiteral["ExpressionStatement"] = "ExpressionStatement"
    expression: OCLExpression

class BindingStatement(Statement):

    type: TypeLiteral["BindingStatement"] = "BindingStatement"
    target: OCLExpression
    value: OCLExpression

class IfStatement(Statement):

    type: TypeLiteral["IfStatement"] = "IfStatement"
    condition: OCLExpression
    then_statements: List["StatementNode"] = Field(default_factory=list)
    else_statements: List["StatementNode"] = Field(default_factory=list)

class ForStatement(Statement):

    type: TypeLiteral["ForStatement"] = "ForStatement"
    iterator: Variable
    collection: OCLExpression
    body: List["StatementNode"] = Field(default_factory=list)

RuleNode = Annotated[
    Union[
        MatchedRule,
        LazyMatchedRule,
        CalledRule
    ],
    Field(discriminator="type")
]

ModuleElementNode = Annotated[
    Union[
        Helper,
        MatchedRule,
        LazyMatchedRule,
        CalledRule
    ],
    Field(discriminator="type")
]


StatementNode = Annotated[
    Union[
        ExpressionStatement,
        BindingStatement,
        IfStatement,
        ForStatement
    ],
    Field(discriminator="type")
]

OutPatternElementNode = Annotated[
    Union[
        SimpleOutPatternElement,
        ForEachOutPatternElement
    ],
    Field(discriminator="type")
]

Helper.model_rebuild()


RuleVariableDeclaration.model_rebuild()

InPatternElement.model_rebuild()
InPattern.model_rebuild()

Binding.model_rebuild()
SimpleOutPatternElement.model_rebuild()
ForEachOutPatternElement.model_rebuild()
OutPattern.model_rebuild()

ExpressionStatement.model_rebuild()
BindingStatement.model_rebuild()
IfStatement.model_rebuild()
ForStatement.model_rebuild()
ActionBlock.model_rebuild()

MatchedRule.model_rebuild()
LazyMatchedRule.model_rebuild()
CalledRule.model_rebuild()

Module.model_rebuild()


class ATLDocument(BaseModel):

    module: Module
