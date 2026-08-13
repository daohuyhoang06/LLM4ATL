import os
from ecore_registry import ATLEcoreRegistry

MODELS_DIR = "d:/LLM4MTLs goc/LLM-based code generation for MTL/LLM-based code generation for MTL/Neuro-Symbolic Pipeline/models/"
bibtex_ecore = os.path.join(MODELS_DIR, "ATL_model/BibTeX.ecore")

registry = ATLEcoreRegistry([bibtex_ecore])
print("Article features:", registry.uml_context.get("Article"))
