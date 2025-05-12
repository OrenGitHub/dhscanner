from __future__ import annotations

import os
import io
import sys
import json
import typing
import tarfile
import pathlib
import logging
import requests
import argparse
import dataclasses

ARGPARSE_PROG_DESC: typing.Final[str] = """

simple dev script to send repo for dhscanner inspection
"""

ARGPARSE_SCAN_DIRNAME_HELP: typing.Final[str] = """
relative / absolute path of the dir you want to scan
"""

ARGPARSE_IGNORE_TESTING_CODE_HELP: typing.Final[str] = """
ignore testing code
"""

ARGPARSE_SHOW_PARSE_STATUS_FOR_FILE_HELP: typing.Final[str] = """
print parse status for file
"""

LOCALHOST: typing.Final[str] = 'http://127.0.0.1'
PORT: typing.Final[int] = 8000

SUFFIXES: typing.Final[set[str]] = {
    'py', 'ts', 'js', 'php', 'rb', 'java', 'cs', 'go'   
}

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s]: %(message)s",
    datefmt="%d/%m/%Y ( %H:%M:%S )",
    stream=sys.stdout
)

def existing_non_empty_dirname(name: str) -> pathlib.Path:

    candidate = pathlib.Path(name)

    if not candidate.is_dir():
        message = f'directory {name} does not exist'
        raise argparse.ArgumentTypeError(message)

    if not any(candidate.iterdir()):
        message = f'no files found in directory: {name}'
        raise argparse.ArgumentTypeError(message)

    return candidate

def existing_fileame(name: str) -> pathlib.Path:

    candidate = pathlib.Path(name)

    if not candidate.is_file():
        message = f'filename {name} does not exist'
        raise argparse.ArgumentTypeError(message)

    return candidate

def proper_bool_value(name: str) -> bool:

    if name not in ['true', 'false']:
        message = f'please specify true | false for including testing code'
        raise argparse.ArgumentTypeError(message)

    return True if name == 'true' else False

@dataclasses.dataclass(frozen=True, kw_only=True)
class Argparse:

    scan_dirname: pathlib.Path
    ignore_testing_code: bool
    show_native_ast_for_file: typing.Optional[pathlib.Path]
    show_parse_status_for_file: typing.Optional[pathlib.Path]

    @staticmethod
    def run() -> typing.Optional[Argparse]:

        logging.info('')
        logging.info('checking required args 👀')
        logging.info('')

        parser = argparse.ArgumentParser(
            description=ARGPARSE_PROG_DESC
        )

        parser.add_argument(
            '--scan_dirname',
            required=True,
            type=existing_non_empty_dirname,
            metavar="dir/you/want/to/scan",
            help=ARGPARSE_SCAN_DIRNAME_HELP
        )

        parser.add_argument(
            '--ignore_testing_code',
            required=True,
            type=proper_bool_value,
            metavar='true | false',
            help=ARGPARSE_IGNORE_TESTING_CODE_HELP
        )

        parser.add_argument(
            '--show_native_ast_for_file',
            required=False,
            type=existing_fileame,
            metavar="some/filename.language",
            help=ARGPARSE_SHOW_PARSE_STATUS_FOR_FILE_HELP
        )

        parser.add_argument(
            '--show_parse_status_for_file',
            required=False,
            type=existing_fileame,
            metavar="some/filename.language",
            help=ARGPARSE_SHOW_PARSE_STATUS_FOR_FILE_HELP
        )

        args = parser.parse_args()

        logging.info('everything is fine 😊')

        return Argparse(
            scan_dirname=args.scan_dirname,
            ignore_testing_code=args.ignore_testing_code,
            show_native_ast_for_file=args.show_native_ast_for_file,
            show_parse_status_for_file=args.show_parse_status_for_file
        )

def relevant(filename: pathlib.Path) -> bool:
    return filename.suffix.lstrip('.') in SUFFIXES

def collect_relevant_files(scan_dirname: pathlib.Path) -> list[pathlib.Path]:

    filenames = []
    for root, _, files in os.walk(scan_dirname):
        for filename in files:
            abspath_filename = pathlib.Path(root) / filename
            if relevant(abspath_filename):
                filenames.append(abspath_filename)

    return filenames

def create_tarfile(filenames: list[pathlib.Path], scan_dirname: pathlib.Path) -> io.BytesIO:

    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode='w:gz') as tar:
        for path in filenames:
            arcname = path.relative_to(scan_dirname)
            tar.add(path, arcname=arcname)

    tar_stream.seek(0)

    logging.info('tar file created 😊')

    return tar_stream

def normalize(
    show_parse_status_for_file: typing.Optional[pathlib.Path],
    scan_dirname: pathlib.Path
) -> typing.Optional[str]:

    if show_parse_status_for_file is None:
        return None

    name = str(show_parse_status_for_file.relative_to(scan_dirname))
    return name.replace('\\', '/')

def create_headers(
    ignore_testing_code: bool,
    show_native_ast_for_file: typing.Optional[str],
    show_parse_status_for_file: typing.Optional[str]
) -> dict:

    headers = {
        'X-Code-Sent-To-External-Server': 'false',
        'X-Ignore-Testing-Code': str(ignore_testing_code),
        'Content-Type': 'application/octet-stream'
    }

    if show_parse_status_for_file is not None:
        headers['X-Show-Parse-Status-For-File'] = show_parse_status_for_file

    if show_native_ast_for_file is not None:
        headers['X-Show-Native-Ast-For-File'] = show_native_ast_for_file

    return headers

def scan(
    ignore_testing_code: bool,
    show_native_ast_for_file: typing.Optional[str],
    show_parse_status_for_file: typing.Optional[str],
    tar_stream: io.BytesIO
) -> dict:

    headers = create_headers(
        ignore_testing_code,
        show_native_ast_for_file,
        show_parse_status_for_file
    )

    return requests.post(
        f'{LOCALHOST}:{PORT}',
        headers=headers,
        data=tar_stream.read()
    )

def main(args: Argparse) -> None:

    files = collect_relevant_files(args.scan_dirname)
    tar_stream = create_tarfile(files, args.scan_dirname)

    show_parse_status_for_file = normalize(
        args.show_parse_status_for_file,
        args.scan_dirname
    )

    show_native_ast_for_file = normalize(
        args.show_native_ast_for_file,
        args.scan_dirname
    )

    response = scan(
        args.ignore_testing_code,
        show_native_ast_for_file,
        show_parse_status_for_file,
        tar_stream
    )

    logging.info(json.dumps(response.json(), indent=4))

if __name__ == "__main__":
    if args := Argparse.run():
        main(args)
