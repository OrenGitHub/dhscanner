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

TO_PHPAST_INIT_CSRF: typing.Final[str] = 'http://127.0.0.1:8001/token'

TO_PHPAST_BUILDER_URL: typing.Final[str] = 'http://127.0.0.1:8001/to/php/ast'
TO_PY_AST_BUILDER_URL: typing.Final[str] = 'http://127.0.0.1:8006/to/native/py/ast'
TO_RB_AST_BUILDER_URL: typing.Final[str] = 'http://127.0.0.1:8007/to/native/cruby/ast'
TO_JS_AST_BUILDER_URL: typing.Final[str] = 'http://127.0.0.1:8000/to/esprima/js/ast'
TO_TS_AST_BUILDER_URL: typing.Final[str] = 'http://127.0.0.1:8008/to/native/ts/ast'

TO_DHSCANNER_AST_BUILDER_FROM_PY_URL: typing.Final[str] = 'http://127.0.0.1:8002/from/py/to/dhscanner/ast'
TO_DHSCANNER_AST_BUILDER_FROM_JS_URL: typing.Final[str] = 'http://127.0.0.1:8002/from/js/to/dhscanner/ast'
TO_DHSCANNER_AST_BUILDER_FROM_TS_URL: typing.Final[str] = 'http://127.0.0.1:8002/from/ts/to/dhscanner/ast'
TO_DHSCANNER_AST_BUILDER_FROM_RB_URL: typing.Final[str] = 'http://127.0.0.1:8002/from/rb/to/dhscanner/ast'
TO_DHSCANNER_AST_BUILDER_FROM_PHPURL: typing.Final[str] = 'http://127.0.0.1:8002/from/php/to/dhscanner/ast'

TO_CODEGEN_URL: typing.Final[str] = 'http://127.0.0.1:8003/codegen'
TO_KBGEN_URL: typing.Final[str] = 'http://127.0.0.1:8004/kbgen'
TO_QENGINE_URL: typing.Final[str] = 'http://127.0.0.1:8005/check'

CVES: typing.Final[list[str]] = [
    'cve_2023_37466',
    'ghsa_97m3',
    'cve_2024_32022',
    'cve_2023_45674',
    'cve_2024_30256',
    'cve_2024_33667',
    'cve_2024_42363',
    'ghsl_2024_093',
    'cve_2024_7856'
]

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

def get_docker_tar_size(args: argparse.Namespace) -> float:
    
    image_tar_name = get_input(args)
    num_bytes = os.path.getsize(image_tar_name)
    return num_bytes / (1024 * 1024 * 1024)

def untar_image_into_workdir(args: argparse.Namespace) -> bool:

    imagename = get_input(args)
    workdir = get_workdir(args)

    imagetar = tarfile.open(name=imagename)
    imagetar.extractall(path=workdir, filter='tar')
    imagetar.close()

    layers = glob.glob(f'{workdir}/**/*', recursive=True)

    for layer in layers:
        if os.path.isfile(layer) and 'POSIX tar archive' in magic.from_file(layer):
            layertar = tarfile.open(name=layer)
            dirname = os.path.dirname(layer)
            layertar.extractall(path=dirname, filter='tar')
            layertar.close()

    # TODO: handle failures and logging
    return True

def third_party_ts_file(filename: str) -> bool:
    return False

def third_party_js_file(filename: str) -> bool:

    third_party_dirs = [
        '/node_modules/',
        '/vendor/',
        '/opt/yarn',
        '/python3/dist-packages',
        '/python3.8/dist-packages',
        '/python3.10/dist-packages',
        '/cuda-12.1/',
        '/python3.11/',
        '/pytorch/',
        '/resources/',
        '/jupyter/',
        '/tutorials/',
        '/nvidia/'
    ]

    return any(subdir in filename for subdir in third_party_dirs)

def collect_js_sources(workdir: str, files: dict[str,list[str]]) -> None:

    filenames = glob.glob(f'{workdir}/**/*.js', recursive=True)
    for filename in filenames:
        if os.path.isfile(filename):
            if not third_party_js_file(filename):
                files['js'].append(filename)

def collect_ts_sources(workdir: str, files: dict[str,list[str]]) -> None:

    filenames = glob.glob(f'{workdir}/**/*.ts', recursive=True)
    for filename in filenames:
        if os.path.isfile(filename):
            if not third_party_ts_file(filename):
                files['ts'].append(filename)

def third_party_php_file(filename: str) -> bool:

    third_party_dirs = ['vendor', '/php/']
    return any(subdir in filename for subdir in third_party_dirs)

def collect_phpsources(workdir: str, files: dict[str,list[str]]) -> None:

    filenames = glob.glob(f'{workdir}/**/*.php', recursive=True)
    for index, filename in enumerate(filenames):
        if not third_party_php_file(filename):
            files['php'].append(filename)

def third_party_py_file(filename: str) -> bool:

    third_party_dirs = [
        '/gdb/',
        '/python/',
        '/python3/',
        '/python3.8/',
        '/python3.10/',
        '/python3.11/',
        '/python3.9/',
        '/pytorch/',
        '/examples/',
        '/tutorials/',
        '/cuda-12.1/',
        '/node_modules/',
        '/nvidia/',
        '/X11/'
    ]

    return any(subdir in filename for subdir in third_party_dirs)

def collect_py_sources(workdir: str, files: dict[str,list[str]]) -> None:

    filenames = glob.glob(f'{workdir}/**/*.py', recursive=True)
    for filename in filenames:
        if not third_party_py_file(filename):
            files['py'].append(filename)

def third_party_rb_file(filename: str) -> bool:

    third_party_dirs = [
        '/python3/',
        '/python3.11/'
    ]

    # return 'zammad' not in filename

    return any(subdir in filename for subdir in third_party_dirs)

def collect_rb_sources(workdir: str, files: dict[str,list[str]]) -> None:

    filenames = glob.glob(f'{workdir}/**/*.rb', recursive=True)
    for filename in filenames:
        if not third_party_rb_file(filename):
            files['rb'].append(filename)

def collect_sources(args: argparse.Namespace):

    workdir = get_workdir(args)
    files: dict[str, list[str]] = collections.defaultdict(list)

    collect_js_sources(workdir, files)
    collect_ts_sources(workdir, files)
    collect_phpsources(workdir, files)
    collect_py_sources(workdir, files)
    collect_rb_sources(workdir, files)

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

def add_ts_ast(filename: str, asts) -> None:

    one_file_at_a_time = read_single_file(filename)
    response = requests.post(TO_TS_AST_BUILDER_URL, files=one_file_at_a_time)
    asts['ts'].append({ 'filename': filename, 'actual_ast': response.text })

def add_py_ast(filename: str, asts) -> None:

    one_file_at_a_time = read_single_file(filename)
    response = requests.post(TO_PY_AST_BUILDER_URL, files=one_file_at_a_time)
    asts['py'].append({ 'filename': filename, 'actual_ast': response.text })

def add_rb_ast(filename: str, asts) -> None:

    one_file_at_a_time = read_single_file(filename)
    response = requests.post(TO_RB_AST_BUILDER_URL, files=one_file_at_a_time)
    asts['rb'].append({ 'filename': filename, 'actual_ast': response.text.replace('\\"', '') })

def add_phpast(filename: str, asts) -> None:

    session = requests.Session()
    response = session.get(TO_PHPAST_INIT_CSRF)
    token = response.text
    cookies = session.cookies
    headers = { 'X-CSRF-TOKEN': token }

    with open(filename) as fl:
        code = fl.read()

    response = session.post(
        TO_PHPAST_BUILDER_URL,
        files={'source': ('source', code)},
        headers=headers,
        cookies=cookies
    )

    logging.debug(response.text)

    asts['php'].append({ 'filename': filename, 'actual_ast': response.text })

def parse_code(files: dict[str, list[str]]):

    asts: dict = collections.defaultdict(list)

    for language, filenames in files.items():
        n = len(filenames)
        for index, filename in enumerate(filenames):
            match language:
                case 'js':  add_js_ast(filename, asts)
                case 'rb':  add_rb_ast(filename, asts)
                case 'py':  add_py_ast(filename, asts)
                case 'ts':  add_ts_ast(filename, asts)
                case 'php': add_phpast(filename, asts)
                case   _  : pass
            
            # logging.info(f'native parsing {index}/{n} {language} files')

    return asts

def add_dhscanner_ast_from_js(filename: str, code, asts) -> None:

    content = { 'filename': filename, 'content': code}
    response = requests.post(TO_DHSCANNER_AST_BUILDER_FROM_JS_URL, json=content)
    asts['js'].append({ 'filename': filename, 'dhscanner_ast': response.text })

def add_dhscanner_ast_from_py(filename: str, code, asts) -> None:

    content = { 'filename': filename, 'content': code}
    response = requests.post(TO_DHSCANNER_AST_BUILDER_FROM_PY_URL, json=content)
    asts['py'].append({ 'filename': filename, 'dhscanner_ast': response.text })

def add_dhscanner_ast_from_ts(filename: str, code, asts) -> None:

    content = { 'filename': filename, 'content': code}
    response = requests.post(TO_DHSCANNER_AST_BUILDER_FROM_TS_URL, json=content)
    asts['ts'].append({ 'filename': filename, 'dhscanner_ast': response.text })

    if filename.endswith('nuxt-link.ts'):
        print(code)
        logging.info(json.dumps(json.loads(response.text), indent=4))


def add_dhscanner_ast_from_rb(filename: str, code, asts) -> None:

    content = { 'filename': filename, 'content': code}
    response = requests.post(TO_DHSCANNER_AST_BUILDER_FROM_RB_URL, json=content)
    asts['rb'].append({ 'filename': filename, 'dhscanner_ast': response.text })

    #if filename.endswith('indie_auth_client.rb'):
    #    print(code)
    #    logging.info(json.dumps(json.loads(response.text), indent=4))

def add_dhscanner_ast_fromphp(filename: str, code, asts) -> None:

    content = { 'filename': filename, 'content': code}
    response = requests.post(TO_DHSCANNER_AST_BUILDER_FROM_PHPURL, json=content)
    asts['php'].append({ 'filename': filename, 'dhscanner_ast': response.text })

    #if filename.endswith('class-sonaar-music.php'):
        # print(code)
        #logging.info(json.dumps(json.loads(response.text), indent=4))

def parse_language_asts(language_asts):

    dhscanner_asts: dict = collections.defaultdict(list)

    for language, asts in language_asts.items():
        n = len(asts)
        for index, ast in enumerate(asts):
            filename = ast['filename']
            code = ast['actual_ast']
            match language:
                case 'js':  add_dhscanner_ast_from_js(filename, code, dhscanner_asts)
                case 'rb':  add_dhscanner_ast_from_rb(filename, code, dhscanner_asts)
                case 'py':  add_dhscanner_ast_from_py(filename, code, dhscanner_asts)
                case 'ts':  add_dhscanner_ast_from_ts(filename, code, dhscanner_asts)
                case 'php': add_dhscanner_ast_fromphp(filename, code, dhscanner_asts)
                case   _  : pass

            # logging.info(f'dhscanner parsing {index}/{n}: {filename}')

    return dhscanner_asts

def codegen(dhscanner_asts):

    content = { 'asts': dhscanner_asts }
    response = requests.post(TO_CODEGEN_URL, json=content)
    return { 'content': response.text }

def kbgen(callables):

    response = requests.post(TO_KBGEN_URL, json=callables)
    return { 'content': response.text }

def query_engine(filename: str):

    just_the_kb_file = read_single_file(filename)
    for cve in CVES:
        url = f'{TO_QENGINE_URL}/{cve}'
        response = requests.post(url, files=just_the_kb_file)
        status = 'looking good 👌 '
        if "yes" in response.text:
            status = 'oh no ! it looks bad 😬😬😬 '
        logging.info(f'[ {cve:<14} ] .............. : {status}')

def main() -> None:

    configure_logger()
    args = parse_args()

    if check(args) == False:
        logging.warning('invalid args - nothing was done 😳 ')
        return

    docker_tar_name = get_input(args)
    docker_tar_size = get_docker_tar_size(args)
    logging.info(f'[ start  ] {docker_tar_name} ({docker_tar_size:.2f} GB) 😃')
    untar_image_into_workdir(args)
    logging.info('[ step 0 ] untar docker image ... : finished 😃 ')

    files = collect_sources(args)
    for language, filenames in files.items():
        logging.debug(f'found {len(filenames)} first party {language} files')

    for language, filenames in files.items():
        for filename in filenames:
            logging.debug(f'collected {language}: {filename}')

    language_asts = parse_code(files)

    logging.info('[ step 1 ] native asts .......... : finished 😃 ')

    dhscanner_asts = parse_language_asts(language_asts)
    valid_dhscanner_asts: dict = collections.defaultdict(list)

    total_num_files: dict[str,int] = collections.defaultdict(int)
    num_parse_errors: dict[str,int] = collections.defaultdict(int)
    for language, asts in dhscanner_asts.items():
        for ast in asts:
            try:
                actual_ast = json.loads(ast['dhscanner_ast'])
                if 'status' in actual_ast and actual_ast['status'] == 'FAILED':
                    num_parse_errors[language] += 1
                    total_num_files[language] += 1
                    continue

            except ValueError:
                continue 

            # file succeeded
            # logging.info(f'{json.dumps(actual_ast, indent=4)}')
            valid_dhscanner_asts[language].append(actual_ast)
            total_num_files[language] += 1

    for language in dhscanner_asts.keys():
        n = total_num_files[language]
        errors = num_parse_errors[language]
        logging.info(f'[ step 2 ] dhscanner ast ( {language} )   : {n - errors}/{n}')

    bitcodes = codegen(
        valid_dhscanner_asts['js'] +
        valid_dhscanner_asts['py'] +
        valid_dhscanner_asts['rb'] +
        valid_dhscanner_asts['php']
    )

    logging.info('[ step 2 ] dhscanner asts ....... : finished 😃 ')
    
    content = bitcodes['content']

    try:
        bitcode_as_json = json.loads(content)
        logging.info('[ step 3 ] code gen ............. : finished 😃 ')
        # logging.info(f'{json.dumps(json.loads(content), indent=4)}')
    except ValueError:
        logging.info('[ step 3 ] code gen ............. : failed 😬 ')
        return

    kb = kbgen(bitcode_as_json)
 
    try: 
        content = json.loads(kb['content'])['content']
        logging.info('[ step 4 ] knowledge base gen ... : finished 😃 ')
    except json.JSONDecodeError:
        logging.warning('[ step 4 ] knowledge base gen ... : failed 😬 ')
        return

    with open('kb.pl', 'w') as fl:
        dummy_classloc = 'not_a_real_loc'
        dummy_classname = "'not_a_real_classnem'"
        fl.write(f'kb_class_name( {dummy_classloc}, {dummy_classname}).\n')
        fl.write('\n'.join(sorted(set(content))))
        fl.write('\n')

    logging.info('[ step 5 ] prolog file gen ...... : finished 😃 ')
    logging.info('[  cves  ] ...................... : starting 🙏 ')

    query_engine('kb.pl')

if __name__ == "__main__":
    main()

