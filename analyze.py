import json
import glob
import requests

def get_python_src_filenames() -> list[str]:
	return glob.glob('code/lib/**/*.py', recursive=True)

def get_python_src_files() -> dict[str, str]:
	python_src_files = {}
	filenames = get_python_src_filenames()
	for filename in filenames:
		with open(filename) as fl:
			python_code = fl.read()
			python_src_files[filename] = python_code

	return python_src_files

def translate(python_code: str) -> str:
    files = {'source': ('source', python_code)}
    response = requests.post('http://localhost:8000/translator/python', files=files)
    return response.text

def parse(python_code: str):
    code = {'filename': 'someFile.txt', 'content': python_code}
    response = requests.post('http://localhost:8001', json=code)
    return response.json()

def get_asts():

    # asts = []
    python_src_files = get_python_src_files()
    for filename, python_code in python_src_files.items():
        translated = translate(python_code)
        return parse(translated)
        # break

    # return asts

def get_callables():

    asts = {'dirname': 'someDir', 'astsContent': [get_asts()] }
    response = requests.post('http://localhost:8002', json=asts)
    return response.json()

def main() -> None:

    callables = get_callables()
    response = requests.post('http://localhost:8003', json=callables)
    print(response.json())

if __name__ == "__main__":
	main()

def old():

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
