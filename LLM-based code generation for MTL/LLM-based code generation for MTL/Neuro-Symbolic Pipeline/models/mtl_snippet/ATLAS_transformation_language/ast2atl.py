import os
import json
import glob

# Mappings to normalize model aliases (case-sensitive)
ALIAS_MAPPING = {
    "families": "Families",
    "persons": "Persons",
    "item": "Item",
    "product": "Product",
    "user": "User",
    "account": "Account",
    "amalthea": "Amalthea",
    "ascet": "Ascet",
    "class": "Class",
    "interface": "Interface",
    "document": "Document",
    "report": "Report",
    "make": "Make",
    "ant": "Ant",
    "bibtex": "BibTeX",
    "docbook": "DocBook",
    "cpl": "CPL",
    "spl": "SPL",
    "dsl": "DSL",
    "km3": "KM3",
    "grafcet": "Grafcet",
    "petrinet": "PetriNet",
    "xml": "XML",
    "network": "Network",
    "graph": "Graph"
}

def normalize_alias(type_str):
    if not type_str:
        return type_str
    
    # Example: families!Member -> Families!Member
    if '!' in type_str:
        parts = type_str.split('!', 1)
        alias = parts[0].lower()
        if alias in ALIAS_MAPPING:
            return f"{ALIAS_MAPPING[alias]}!{parts[1]}"
    
    # Standalone alias like in 'create OUT : Target from IN : Source'
    alias_lower = type_str.lower()
    if alias_lower in ALIAS_MAPPING:
        return ALIAS_MAPPING[alias_lower]
        
    return type_str

class ATLGenerator:
    def __init__(self, ast):
        self.ast = ast

    def generate(self):
        return self._visit(self.ast)

    def _visit(self, node):
        if not isinstance(node, dict):
            return str(node)
            
        node_type = node.get("type")
        method_name = f"_visit_{node_type}"
        visitor = getattr(self, method_name, self._default_visit)
        return visitor(node)

    def _default_visit(self, node):
        return f"/* UNKNOWN NODE TYPE: {node.get('type')} */"

    def _visit_Module(self, node):
        name = node.get("name", "UnnamedModule")
        lines = [f"module {name};\n"]
        
        # Models
        out_models = []
        for om in node.get("output_models", []):
            alias = "OUT"
            meta = normalize_alias(om.get("metamodel", ""))
            out_models.append(f"{alias} : {meta}")
            
        in_models = []
        for im in node.get("input_models", []):
            alias = "IN"
            meta = normalize_alias(im.get("metamodel", ""))
            in_models.append(f"{alias} : {meta}")
            
        lines.append(f"create {', '.join(out_models)} from {', '.join(in_models)};\n\n")
        
        # Elements (Helpers & Rules)
        for el in node.get("elements", []):
            lines.append(self._visit(el))
            lines.append("\n\n")
            
        return "".join(lines)

    def _visit_Helper(self, node):
        kind = node.get("kind", "attribute")
        context = normalize_alias(node.get("context_type", ""))
        name = node.get("name", "")
        params = node.get("parameters", [])
        return_type = normalize_alias(node.get("return_type", ""))
        body = self._visit(node.get("body", {}))
        
        ctx_str = f"context {context} " if context else ""
        
        # If it's an operation or has parameters, add ()
        if kind == "operation" or params:
            param_strs = []
            for p in params:
                p_name = p.get("name", "")
                p_type = normalize_alias(p.get("type", ""))
                param_strs.append(f"{p_name} : {p_type}")
            name_with_params = f"{name}({', '.join(param_strs)})"
        else:
            name_with_params = name
            
        lines = []
        lines.append(f"helper {ctx_str}def: {name_with_params} : {return_type} =")
        
        # Indent body
        body_lines = body.split("\n")
        for i, bl in enumerate(body_lines):
            lines.append(f"    {bl}")
            
        res = "\n".join(lines)
        if not res.endswith(";"):
            res += ";"
        return res

    def _visit_MatchedRule(self, node):
        name = node.get("name", "")
        lines = [f"rule {name} {{"]
        
        # In pattern
        in_pattern = node.get("in_pattern", {})
        if in_pattern:
            lines.append(self._visit(in_pattern))
            
        # Out pattern
        out_pattern = node.get("out_pattern", {})
        if out_pattern:
            lines.append(self._visit(out_pattern))
            
        lines.append("}")
        return "\n".join(lines)

    def _visit_LazyMatchedRule(self, node):
        name = node.get("name", "")
        lines = [f"lazy rule {name} {{"]
        
        # In pattern
        in_pattern = node.get("in_pattern", {})
        if in_pattern:
            lines.append(self._visit(in_pattern))
            
        # Out pattern
        out_pattern = node.get("out_pattern", {})
        if out_pattern:
            lines.append(self._visit(out_pattern))
            
        lines.append("}")
        return "\n".join(lines)

    def _visit_InPattern(self, node):
        lines = ["    from"]
        for el in node.get("elements", []):
            lines.append(f"        {self._visit(el)}")
            
        filter_expr = node.get("filter")
        if filter_expr:
            # We add filter to the last element
            lines[-1] += f" (\n            {self._visit(filter_expr)}\n        )"
        return "\n".join(lines)

    def _visit_InPatternElement(self, node):
        var = node.get("variable", {})
        var_name = var.get("name", "")
        type_name = normalize_alias(var.get("declared_type", ""))
        return f"{var_name} : {type_name}"

    def _visit_SimpleInPatternElement(self, node):
        var_name = node.get("var_name", "")
        type_name = normalize_alias(node.get("type", ""))
        return f"{var_name} : {type_name}"

    def _visit_OutPattern(self, node):
        lines = ["    to"]
        els = node.get("elements", [])
        for i, el in enumerate(els):
            el_str = self._visit(el)
            separator = "," if i < len(els) - 1 else ""
            lines.append(f"        {el_str}{separator}")
        return "\n".join(lines)

    def _visit_SimpleOutPatternElement(self, node):
        var = node.get("variable", {})
        if var:
            var_name = var.get("name", "")
            type_name = normalize_alias(var.get("declared_type", ""))
        else:
            var_name = node.get("var_name", "")
            type_name = normalize_alias(node.get("type", ""))
            
        lines = [f"{var_name} : {type_name} ("]
        
        bindings = node.get("bindings", [])
        for i, b in enumerate(bindings):
            sep = "," if i < len(bindings) - 1 else ""
            lines.append(f"            {self._visit(b)}{sep}")
            
        lines.append("        )")
        return "\n".join(lines)

    def _visit_Binding(self, node):
        prop = node.get("property_name", "")
        val = self._visit(node.get("value", {}))
        return f"{prop} <- {val}"

    # OCL Expressions
    def _visit_LiteralExpression(self, node):
        val = node.get("value", "")
        lit_type = node.get("literal_type", "")
        if lit_type == "String" or isinstance(val, str):
            return f"'{val}'"
        elif lit_type == "Boolean":
            return "true" if val else "false"
        return str(val)
    def _visit_IfExpression(self, node):
        cond = self._visit(node.get("condition", {}))
        then_expr = self._visit(node.get("then_expression", {}))
        else_expr = self._visit(node.get("else_expression", {}))
        
        lines = [
            f"if {cond} then",
            f"    {then_expr}",
            f"else",
            f"    {else_expr}",
            f"endif"
        ]
        return "\n".join(lines)

    def _visit_BinaryExpression(self, node):
        left = self._visit(node.get("left", {}))
        op = node.get("operator", "")
        right = self._visit(node.get("right", {}))
        return f"({left} {op} {right})"

    def _visit_UnaryExpression(self, node):
        op = node.get("operator", "")
        expr = self._visit(node.get("expression", {}))
        return f"{op} {expr}"

    def _visit_PropertyCall(self, node):
        src = self._visit(node.get("source", {}))
        prop = node.get("property_name", "")
        return f"{src}.{prop}"

    def _visit_OperationCall(self, node):
        src = self._visit(node.get("source", {}))
        op = node.get("operation_name", "")
        args = [self._visit(a) for a in node.get("arguments", [])]
        args_str = ", ".join(args)
        if src:
            return f"{src}.{op}({args_str})"
        else:
            return f"{op}({args_str})"

    def _visit_CollectionOperation(self, node):
        src = self._visit(node.get("source", {}))
        op = node.get("operation_name", "")
        args = [self._visit(a) for a in node.get("arguments", [])]
        args_str = ", ".join(args)
        if src:
            return f"{src}->{op}({args_str})"
        else:
            return f"->{op}({args_str})"

    def _visit_CollectionLiteral(self, node):
        kind = node.get("collection_kind", "Set")
        els = [self._visit(e) for e in node.get("elements", [])]
        return f"{kind}{{{', '.join(els)}}}"

    def _visit_IteratorExpression(self, node):
        src = self._visit(node.get("source", {}))
        name = node.get("iterator_type", node.get("name", "select"))
        iterators = node.get("iterators", [])
        
        iter_strs = []
        for it in iterators:
            if isinstance(it, dict):
                it_name = it.get("name", "")
                iter_strs.append(it_name)
            else:
                iter_strs.append(str(it))
                
        iters_joined = ", ".join(iter_strs)
        body = self._visit(node.get("body", {}))
        return f"{src}->{name}({iters_joined} | {body})"

    def _visit_Variable(self, node):
        name = str(node.get("name", ""))
        if "!" in name:
            name = normalize_alias(name)
        return name

    def _visit_StringLiteral(self, node):
        val = node.get("value", "")
        return f"'{val}'"

    def _visit_IntegerLiteral(self, node):
        return str(node.get("value", 0))

    def _visit_RealLiteral(self, node):
        return str(node.get("value", 0.0))

    def _visit_BooleanLiteral(self, node):
        return "true" if node.get("value") else "false"
        
    def _visit_EnumLiteral(self, node):
        val = node.get("value", "")
        return f"#{val}"
        
    def _visit_OclUndefined(self, node):
        return "OclUndefined"

    def _visit_SequenceExpression(self, node):
        els = [self._visit(e) for e in node.get("elements", [])]
        return f"Sequence{{{', '.join(els)}}}"
        
    def _visit_SetExpression(self, node):
        els = [self._visit(e) for e in node.get("elements", [])]
        return f"Set{{{', '.join(els)}}}"

    def _visit_LetExpression(self, node):
        variables = node.get("variables", [])
        in_expr = self._visit(node.get("in_expression", {}))
        
        lines = ["let"]
        for i, v in enumerate(variables):
            v_name = v.get("name", "")
            v_type = normalize_alias(v.get("type", ""))
            v_init = self._visit(v.get("init_expression", {}))
            
            type_decl = f" : {v_type}" if v_type else ""
            lines.append(f"    {v_name}{type_decl} = {v_init}")
            
            if i < len(variables) - 1:
                lines[-1] += ","
                
        lines.append("in")
        lines.append(f"    {in_expr}")
        return "\n".join(lines)


def process_all_ast():
    ast_dir = os.path.join(os.path.dirname(__file__), "responses", "ast")
    out_dir = os.path.join(os.path.dirname(__file__), "responses", "ast2atl")
    os.makedirs(out_dir, exist_ok=True)
    
    json_files = glob.glob(os.path.join(ast_dir, "*.json"))
    print(f"Found {len(json_files)} AST files to convert.")
    
    for jf in json_files:
        basename = os.path.basename(jf)
        name, _ = os.path.splitext(basename)
        out_file = os.path.join(out_dir, f"{name}.atl")
        
        try:
            with open(jf, "r", encoding="utf-8") as f:
                ast = json.load(f)
                
            generator = ATLGenerator(ast)
            atl_code = generator.generate()
            
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(atl_code)
            print(f"[OK] Generated {out_file}")
        except Exception as e:
            print(f"[ERROR] Failed to generate {basename}: {e}")

if __name__ == "__main__":
    process_all_ast()
