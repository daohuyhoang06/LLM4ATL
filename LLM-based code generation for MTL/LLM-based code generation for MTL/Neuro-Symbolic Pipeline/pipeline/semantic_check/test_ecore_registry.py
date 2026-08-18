from ecore_registry import ATLEcoreRegistry
from errors import SemanticError
import json

registry = ATLEcoreRegistry("../ATL_model/Grafcet.ecore")

print(registry.resolve_property("Step", "isActive"))

try:
    registry.resolve_property("Step", "isActive")
except SemanticError as e:
    print("Semantic Error:", e)