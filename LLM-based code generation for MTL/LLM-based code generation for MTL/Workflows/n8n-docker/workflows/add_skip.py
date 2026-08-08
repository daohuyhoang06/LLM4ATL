import json

with open('Prompting_atl_ast.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Create Check File Exists node
check_node = {
  'parameters': {
    'command': 'test -f "/data/snippets/ATLAS_transformation_language/responses/ast/{{ $json.baseName }}.json" && echo "true" || echo "false"'
  },
  'type': 'n8n-nodes-base.executeCommand',
  'typeVersion': 1,
  'position': [1200, 100],
  'id': 'check_file_exists_id',
  'name': 'Check File Exists'
}

# Create If node
if_node = {
  'parameters': {
    'conditions': {
      'string': [
        {
          'value1': '={{ $json.stdout.trim() }}',
          'value2': 'false'
        }
      ]
    }
  },
  'type': 'n8n-nodes-base.if',
  'typeVersion': 1,
  'position': [1400, 100],
  'id': 'skip_if_exists_id',
  'name': 'Skip if exists'
}

wf['nodes'].extend([check_node, if_node])

# Update connections
if 'Merge' in wf['connections']:
    wf['connections']['Merge']['main'] = [[{'node': 'Check File Exists', 'type': 'main', 'index': 0}]]

wf['connections']['Check File Exists'] = {
    'main': [[{'node': 'Skip if exists', 'type': 'main', 'index': 0}]]
}

wf['connections']['Skip if exists'] = {
    'main': [
        [{'node': 'Generate AST JSON', 'type': 'main', 'index': 0}],
        [{'node': 'Loop Over Items', 'type': 'main', 'index': 0}]
    ]
}

# Generate AST JSON position update for better layout
for n in wf['nodes']:
    if n['name'] == 'Generate AST JSON':
        n['position'] = [1600, -50]
    if n['name'] == 'Convert response to File':
        n['position'] = [1800, -50]
    if n['name'] == 'Write response to disk':
        n['position'] = [2000, -50]

with open('Prompting_atl_ast.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2)

print('Added skip logic to Prompting_atl_ast.json')
