import json
import glob
import requests

# this is my lovely new comment

def get_python_src_filenames() -> list[str]:
    return glob.glob('code_tag/*.py', recursive=True)

def get_python_src_files() -> dict[str, str]:
	python_src_files = {}
	filenames = get_python_src_filenames()
	for filename in filenames:
		with open(filename) as fl:
			python_code = fl.read()
			python_src_files[filename] = python_code

	return python_src_files

def translate(filename: str, python_code: str) -> str:
    files = {'source': ('source', python_code)}
    response = requests.post('http://localhost:8000/translator/python', files=files)
    # print(f'translation: {filename} -> {response.status_code}')
    #if 'oren' in filename:
    #    print(response.text)
    return response.text

def parse(filename:str, python_code: str):
    code = {'filename': filename, 'content': python_code}
    response = requests.post('http://localhost:8001', json=code)
    # print(f'parsing:     {filename} -> {response.status_code}')
    return response.json()

def get_asts():

    asts = []
    python_src_files = get_python_src_files()
    for filename, python_code in python_src_files.items():
        translated = translate(filename, python_code)
        asts.append(parse(filename, translated))

    return asts

def get_callables():

    asts = {'dirname': 'someDir', 'astsContent': get_asts() }
    response = requests.post('http://localhost:8002', json=asts)
    return response.json()

def main() -> None:

    #callables = get_callables()
    asts = get_asts()
    for ast in asts:
        content = json.loads(json.dumps(ast))
        if isinstance(content, dict) and 'filename' in content:
            filename = content['filename']
            print(f'{filename} ---> SUCCESS')
        else:
            print(json.dumps(ast))

    #callables = get_callables()
    #response = requests.post('http://localhost:8003', json=callables)
    #print(response.json())

if __name__ == "__main__":
	main()

