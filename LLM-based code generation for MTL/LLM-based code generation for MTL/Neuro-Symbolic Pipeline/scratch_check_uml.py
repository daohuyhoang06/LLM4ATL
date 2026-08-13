import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'models'))

from semantic_check.ecore_registry import ATLEcoreRegistry

registry = ATLEcoreRegistry([
    os.path.join(current_dir, 'models', 'ATL_model', 'amalthea.ecore'),
    os.path.join(current_dir, 'models', 'ATL_model', 'ascet.ecore')
])

print("SoftwareTask in registry:", "SoftwareTask" in registry.uml_context)
if "SoftwareTask" in registry.uml_context:
    print("Super class:", registry.uml_context["SoftwareTask"].get("super_class"))

print("Task in registry:", "Task" in registry.uml_context)
if "Task" in registry.uml_context:
    print("Super class:", registry.uml_context["Task"].get("super_class"))
