from type_environment import TypeEnvironment
from errors import SemanticError

import json

env = TypeEnvironment()

env.register_rule(
    name="Task2SoftwareTask",
    parameter_types=["amalthea!Task"],
    output_types=["ascet!SoftwareTask"],
    rule_kind="LazyMatchedRule"
)

print(json.dumps(env.rules))