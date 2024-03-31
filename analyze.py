import os
import json
import glob
import tarfile
import requests

# dev imports
from typing import Final

# routes
TO_NATIVE_JS_AST_ROUTE: Final[str] = 'http://localhost:8000/to/native/ast'
TO_DHSCANNER_AST_ROUTE: Final[str] = 'http://localhost:8000/to/dhscanner/ast'

def get_src_filenames(dirname: str, suffix: str) -> list[str]:
    return glob.glob(f"{dirname}/*.{suffix}", recursive=True)

def get_src_files(dirname: str, suffix: str) -> dict[str, str]:
    src_files = {}
    filenames = get_src_filenames(suffix)
    for filename in filenames:
        with open(filename) as fl:
            code = fl.read()
            src_files[filename] = code

    return python_src_files

def to_native_js_ast(js_code: str) -> str:
    files = {'source': ('source', js_code)}
    response = requests.post(TO_NATIVE_JS_AST_ROUTE, files=files)
    return response.text

def from_js_ast_to_dhscanner_ast(js_filename:str, js_code: str):
    code = {'filename': js_filename, 'content': js_code}
    response = requests.post(TO_DHSCANNER_AST_ROUTE, json=code)
    return response.json()

def get_asts(dirname: str, suffix: str, to_native_ast, to_dhscanner_ast):

    asts = []
    src_files = get_src_files(dirname, suffix)
    for filename, code in src_files.items():
        native_ast = to_native_ast(filename, code)
        asts.append(to_dhscanner_ast(filename, native_ast))

    return asts

def analyze():

    asts = get_asts('dockers/example_00', 'js', to_nativ_js_ast, from_native_js_ast_to_dhscanner_ast)
    for ast in asts:
        content = json.loads(json.dumps(ast))
        if isinstance(content, dict) and 'filename' in content:
            filename = content['filename']
            print(f'{filename} ---> SUCCESS')
        else:
            print(json.dumps(ast))

def main():

    workdir = 'dockers/example_00'
    tar_ed_docker = tarfile.open(name=f'{workdir}/example.tar')
    tar_ed_docker.extractall(path=workdir)
    tar_ed_docker.close()

    dirnames = []    
    layers = glob.glob(f'{workdir}/**/layer.tar', recursive=True)
    for layer in layers:
        tar_ed_layer = tarfile.open(name=layer)
        dirname = os.path.dirname(layer)
        tar_ed_layer.extractall(path=dirname)
        tar_ed_layer.close()
        dirnames.append(dirname)

    print(dirnames)

    for dirname in dirnames:
        js_files = glob.glob(f'{dirname}/**/*.js', recursive=True)
        for js_file in js_files:
            if 'node_modules' not in js_file:
                print(js_file)

if __name__ == "__main__":
    main()

