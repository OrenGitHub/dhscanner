import os
import sys
import json
import glob
import magic
import typing
import tarfile
import logging
import requests
import argparse
import collections

ARGPARSE_PROG_DESC: typing.Final[str] = 'docker container scanner'
ARGPARSE_INPUT_HELP: typing.Final[str] = "docker image saved as *.tar file"
ARGPARSE_WORKDIR_HELP: typing.Final[str] = """
the tar file content is extracted to the workdir and manipulated there.
ideally, this is a new (non exiting) directory.
if you want to override an existing directory (say from a previous scan),
you have to explictly say so with the flag --force
"""

ARGPARSE_ERASE_OLD_WORKDIR: typing.Final[str] = """
use this flag in combination with --workdir, when you want to erase
an existing directory (say from a previous scan)
"""

DEFAULT_INPUT_NAME: typing.Final[str] = "nonexisting.tar"
DEFAULT_WORKDIR_NAME: typing.Final[str] = "workdir"

# which component listens on which port
SERVICE_NAME: typing.Final[dict[int,str]] = {
    8000: 'front.js',
    8001: 'front.rb',
    8002: 'parser.js',
    8003: 'parser.rb',
    8004: 'codegen',
    8006: 'kbgen'
}

TO_JS_AST_BUILDER_URL: typing.Final[str] = 'http://127.0.0.1:8000/to/esprima/js/ast'
TO_DHSCANNER_AST_BUILDER_FROM_JS_URL: typing.Final[str] = 'http://127.0.0.1:8002/to/dhscanner/ast'
TO_CODEGEN_URL: typing.Final[str] = 'http://127.0.0.1:8004/codegen'
TO_KBGEN_URL: typing.Final[str] = 'http://127.0.0.1:8006/kbgen'

def existing_tarfile(candidate) -> str:

    if os.path.isfile(candidate):
        if candidate.endswith('.tar'):
            return candidate

    raise argparse.ArgumentTypeError(
        f'\n\nERROR: nonexisting or invalid tar file: {candidate}\n'
    )

def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=ARGPARSE_PROG_DESC
    )

    parser.add_argument(
        '--input',
        required=True,
        nargs=1,
        metavar="<image>.tar",
        type=existing_tarfile,
        help=ARGPARSE_INPUT_HELP
    )
    
    parser.add_argument(
        '--workdir',
        required=True,
        nargs=1,
        type=str,
        help=ARGPARSE_WORKDIR_HELP
    )

    parser.add_argument(
        '--force',
        action=argparse.BooleanOptionalAction,
        required=False,
        help=ARGPARSE_ERASE_OLD_WORKDIR
    )

    return parser.parse_args()

def get_workdir(args: argparse.Namespace) -> str:

    args_workdir = args.workdir

    if not isinstance(args_workdir, list):
        return DEFAULT_WORKDIR_NAME

    if len(args_workdir) != 1:
        return DEFAULT_WORKDIR_NAME

    return args_workdir[0]

def get_input(args: argparse.Namespace) -> str:

    args_input = args.input
    if not isinstance(args_input, list):
        return DEFAULT_INPUT_NAME

    if len(args_input) != 1:
        return DEFAULT_INPUT_NAME

    return args_input[0]

def check_workdir_new_or_erasable(args) -> bool:

    args_workdir = get_workdir(args)
    
    if os.path.exists(args_workdir):
        if args.force:
            os.rmdir(args_workdir)
        else:
            logging.warning('specified workdir already exists !')
            logging.warning('did you forget to specify --force ?')
            return False
    
    os.mkdir(args_workdir)
    return True

def check(args: argparse.Namespace) -> bool:
    return check_workdir_new_or_erasable(args)

def untar_image_into_workdir(args: argparse.Namespace) -> bool:

    imagename = get_input(args)
    workdir = get_workdir(args)

    imagetar = tarfile.open(name=imagename)
    imagetar.extractall(path=workdir)
    imagetar.close()

    layers = glob.glob(f'{workdir}/**/*', recursive=True)

    for layer in layers:
        if os.path.isfile(layer) and 'POSIX tar archive' in magic.from_file(layer):
            layertar = tarfile.open(name=layer)
            dirname = os.path.dirname(layer)
            layertar.extractall(path=dirname)
            layertar.close()

    # TODO: handle failures and logging
    return True

def third_party_js_file(filename: str) -> bool:

    third_party_dirs = ['node_modules', '/opt/yarn', 'python3/dist-packages']
    return any(subdir in filename for subdir in third_party_dirs)

def collect_js_sources(workdir: str, files: dict[str,list[str]]) -> None:

    filenames = glob.glob(f'{workdir}/**/*.js', recursive=True)
    for filename in filenames:
        if not third_party_js_file(filename):
            files['js'].append(filename)

def collect_sources(args: argparse.Namespace):

    workdir = get_workdir(args)
    files: dict[str, list[str]] = collections.defaultdict(list)

    collect_js_sources(workdir, files)
    # collect_rb_sources(files)
    # collect_py_sources(files)
    # collect_ts_sources(files)
    # collect_phpsources(files)

    return files

def configure_logger() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s]: %(message)s",
        datefmt="%d/%m/%Y ( %H:%M:%S )",
        stream=sys.stdout
    )

def read_single_file(filename: str):

    with open(filename) as fl:
        code = fl.read()

    return { 'source': ('source', code) }

def add_js_ast(filename: str, asts) -> None:

    one_file_at_a_time = read_single_file(filename)
    response = requests.post(TO_JS_AST_BUILDER_URL, files=one_file_at_a_time)
    asts['js'].append({ 'filename': filename, 'actual_ast': response.text })

def parse_code(files: dict[str, list[str]]):

    asts: dict = collections.defaultdict(list)

    for language, filenames in files.items():
        for filename in filenames:
            match language:
                case 'js':  add_js_ast(filename, asts)
                case 'rb':  add_js_ast(filename, asts)
                case 'py':  add_js_ast(filename, asts)
                case 'ts':  add_js_ast(filename, asts)
                case 'php': add_js_ast(filename, asts)
                case   _  : pass

    return asts

def add_dhscanner_ast_from_js(filename: str, code, asts):

    content = { 'filename': filename, 'content': code}
    response = requests.post(TO_DHSCANNER_AST_BUILDER_FROM_JS_URL, json=content)
    asts['js'].append({ 'filename': filename, 'dhscanner_ast': response.text })

def parse_language_asts(language_asts):

    dhscanner_asts: dict = collections.defaultdict(list)

    for language, asts in language_asts.items():
        for ast in asts:
            filename = ast['filename']
            code = ast['actual_ast']
            match language:
                case 'js':  add_dhscanner_ast_from_js(filename, code, dhscanner_asts)
                case 'rb':  add_dhscanner_ast_from_js(filename, code, dhscanner_asts)
                case 'py':  add_dhscanner_ast_from_js(filename, code, dhscanner_asts)
                case 'ts':  add_dhscanner_ast_from_js(filename, code, dhscanner_asts)
                case 'php': add_dhscanner_ast_from_js(filename, code, dhscanner_asts)
                case   _  : pass

    return dhscanner_asts

def codegen(dhscanner_asts):

    content = { 'dirname': 'GGG', 'astsContent': dhscanner_asts }
    response = requests.post(TO_CODEGEN_URL, json=content)
    return { 'content': response.text }

def kbgen(callables):

    response = requests.post(TO_KBGEN_URL, json=callables)
    return { 'content': response.text }

def main() -> None:

    configure_logger()
    args = parse_args()

    if check(args) == False:
        logging.warning('invalid args - nothing was done 😳 ')
        return

    logging.info('everything looks great - starting to untar 😃 ')
    untar_image_into_workdir(args)
    logging.info('everything looks great - finished untar 😃 ')

    files = collect_sources(args)
    for language, filenames in files.items():
        logging.info(f'found {len(filenames)} first party {language} files')

    for language, filenames in files.items():
        for filename in filenames:
            logging.debug(f'collected {language}: {filename}')

    language_asts = parse_code(files)
    dhscanner_asts = parse_language_asts(language_asts)
    valid_dhscanner_asts: dict = collections.defaultdict(list)

    total_num_files: dict[str,int] = collections.defaultdict(int)
    num_parse_errors: dict[str,int] = collections.defaultdict(int)
    for language, asts in dhscanner_asts.items():
        for ast in asts:
            actual_ast = json.loads(ast['dhscanner_ast'])
            if 'status' in actual_ast and actual_ast['status'] == 'FAILED':
                num_parse_errors[language] += 1
                total_num_files[language] += 1
            else:
                logging.debug(f'{json.dumps(actual_ast, indent=4)}')
                valid_dhscanner_asts[language].append(actual_ast)
                total_num_files[language] += 1

    logging.info(f'parse errors: {json.dumps(num_parse_errors)}')
    logging.info(f'total num files: {json.dumps(total_num_files)}')

    bitcodes = codegen(valid_dhscanner_asts['js'])
    content = bitcodes['content']
    # logging.debug(f'{json.dumps(json.loads(content), indent=4)}')

    kb = kbgen(json.loads(content))
    content = json.loads(kb['content'])['content']

    with open('kb.pl', 'w') as fl:
        fl.write('\n'.join(content))
        fl.write('\n')

    logging.info('wrote knowledge base: kb.pl')

if __name__ == "__main__":
    main()

