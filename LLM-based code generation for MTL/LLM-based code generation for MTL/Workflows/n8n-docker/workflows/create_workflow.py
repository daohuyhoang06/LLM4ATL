import json
import os

with open('Prompting_atl.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

wf['name'] = 'Prompting_ATL_AST'
wf['id'] = 'Prompting_ATL_AST_ID'

# Remove unnecessary nodes
nodes_to_remove = ['Few_shot', 'Grammar', 'Helper_methods', 'Read helper methods', 'Extract text from helper methods', 'Set Parameters']
wf['nodes'] = [n for n in wf['nodes'] if n['name'] not in nodes_to_remove]

# Modify specific nodes
for node in wf['nodes']:
    if node['name'] == 'Read few shot examples':
        node['name'] = 'Read system prompt'
        node['parameters']['fileSelector'] = '=/data/neuro-symbolic/system_prompt.txt'
    elif node['name'] == 'Extract text from examples file':
        node['name'] = 'Extract text from system prompt'
        node['parameters']['destinationKey'] = 'system_prompt'
    elif node['name'] == 'Read Grammar':
        node['name'] = 'Read schema'
        node['parameters']['fileSelector'] = '=/data/neuro-symbolic/schema/atl_schema.json'
    elif node['name'] == 'Extract text from grammar':
        node['name'] = 'Extract text from schema'
        node['parameters']['destinationKey'] = 'schema'
    elif node['name'] == 'Merge':
        node['parameters']['numberInputs'] = 4
    elif node['name'] == '(Re-)Generate code':
        node['name'] = 'Generate AST JSON'
        node['parameters']['text'] = '''={{ $json.prompt }}

-- End of request.
Here are the Ecore models for the source and target metamodels:
{{ $json.model }}

The models are located here:
"http://vitruv.tools/methodologisttemplate/[modelname]"

Based on the above transformation requirements and the provided metamodels, generate the full Abstract Syntax Tree (AST) of the corresponding ATL transformation.
Remember:
- Your response must be ONLY a valid JSON object matching the `ATLDocument` schema.
- Do not include any explanations, markdown code blocks, or raw ATL code.'''
        node['parameters']['messages']['messageValues'][0]['message'] = '''={{ $json.system_prompt.replace('{{ $json.ast_schema }}', $json.schema) }}'''
    elif node['name'] == 'Write response to disk':
        node['parameters']['fileName'] = '=/data/snippets/ATLAS_transformation_language/responses/ast/{{ $node["Save file name"].json.baseName }}.json'
        node['parameters']['dataPropertyName'] = '={{$node["Generate AST JSON"].json.text}}'
    elif node['name'] == 'Loop Over Items':
        pass

# Fix connections
new_connections = {}
for source_node, targets in wf['connections'].items():
    if source_node in nodes_to_remove:
        continue
    
    new_source = source_node
    if source_node == 'Read few shot examples': new_source = 'Read system prompt'
    elif source_node == 'Extract text from examples file': new_source = 'Extract text from system prompt'
    elif source_node == 'Read Grammar': new_source = 'Read schema'
    elif source_node == 'Extract text from grammar': new_source = 'Extract text from schema'
    elif source_node == '(Re-)Generate code': new_source = 'Generate AST JSON'

    new_targets = {}
    for conn_type, outputs in targets.items():
        new_outputs = []
        for output_list in outputs:
            new_output_list = []
            for target in output_list:
                target_name = target['node']
                if target_name in nodes_to_remove:
                    continue
                if target_name == 'Read few shot examples': target_name = 'Read system prompt'
                elif target_name == 'Extract text from examples file': target_name = 'Extract text from system prompt'
                elif target_name == 'Read Grammar': target_name = 'Read schema'
                elif target_name == 'Extract text from grammar': target_name = 'Extract text from schema'
                elif target_name == '(Re-)Generate code': target_name = 'Generate AST JSON'
                
                target['node'] = target_name
                new_output_list.append(target)
            new_outputs.append(new_output_list)
        new_targets[conn_type] = new_outputs
    new_connections[new_source] = new_targets

wf['connections'] = new_connections

# Add direct connection from Loop Over Items to Read system prompt and Read schema
loop_outputs = wf['connections']['Loop Over Items']['main'][1]
# Clear existing ones just in case and put what we need
new_loop_outputs = [o for o in loop_outputs if o['node'] not in ['Read Grammar', 'Read few shot examples', 'Read helper methods', 'Set Parameters']]
new_loop_outputs.append({'node': 'Read system prompt', 'type': 'main', 'index': 0})
new_loop_outputs.append({'node': 'Read schema', 'type': 'main', 'index': 0})
wf['connections']['Loop Over Items']['main'][1] = new_loop_outputs

with open('Prompting_atl_ast.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2)
print('Done!')
