import json
import requests

code ="""
int xxx;
int yyy;
"""

#with open('ast2.json') as fl:
#	asts = json.load(fl)

#print(json.dumps(asts, indent=4))

# asts_data = {'dirname': '/some/arbitrary/dir', 'astsContent': asts}
code_data = {'filename': 'someFile.txt', 'content': code}

response = requests.post('http://localhost:8000', json=code_data)
# response = requests.post('http://localhost:8000', json=asts_data)

print(response)

json_response = json.loads(response.json())
#print(json.dumps(json_response, indent=4))

x = {'dirname': 'some/bullshit/dir', 'astsContent': [json_response]}
response = requests.post('http://localhost:8001', json=x)

#print(response)
json_response = json.loads(response.json())
print(json.dumps(json_response, indent=4))