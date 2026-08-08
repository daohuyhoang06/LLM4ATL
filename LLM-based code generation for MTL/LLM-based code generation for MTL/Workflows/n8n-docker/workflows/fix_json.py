import json
with open('Prompting_atl_ast.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for node in wf['nodes']:
    if node['name'] == 'Generate AST JSON':
        new_text = '''={{ $json.system_prompt.replace('<INSERT_SCHEMA_HERE>', $json.schema) }}

=== ECORE MODELS ===
{{ $json.model }}

=== TRANSFORMATION REQUEST ===
{{ $json.prompt }}'''
        
        node['parameters']['text'] = new_text

with open('Prompting_atl_ast.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2)

print('Updated Prompting_atl_ast.json')
