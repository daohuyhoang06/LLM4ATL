import json
with open('Prompting_atl_ast.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

for node in wf['nodes']:
    if node['name'] == 'Read system prompt':
        node['parameters']['fileSelector'] = '/data/neuro-symbolic/system_prompt.txt'
    elif node['name'] == 'Read schema':
        node['parameters']['fileSelector'] = '/data/neuro-symbolic/schema/atl_schema.json'
    elif node['name'] == 'Convert response to File':
        node['parameters']['binaryPropertyName'] = 'data'
    elif node['name'] == 'Write response to disk':
        node['parameters']['dataPropertyName'] = 'data'
        node['parameters']['fileName'] = '=/data/snippets/ATLAS_transformation_language/responses/ast/{{ $node["Save file name"].json.baseName }}.json'

with open('Prompting_atl_ast.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2)

print('Updated Prompting_atl_ast.json')
