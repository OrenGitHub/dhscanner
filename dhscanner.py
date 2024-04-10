import os
import json
import glob
import typing
import tarfile
import requests
import argparse

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

def check_workdir_new_or_erasable(args) -> bool:

    args_workdir = args.workdir
    if not isinstance(args_workdir, list):
        return False

    if len(args_workdir) != 1:
        return False

    workdir = args_workdir[0]
    
    if os.path.exists(workdir):
        if args.force:
            os.rmdir(workdir)
        else:
            return False
    
    os.mkdir(workdir)
    return True

def check(args: argparse.Namespace) -> bool:
    return check_workdir_new_or_erasable(args)

def main() -> None:

    args = parse_args()
    if check(args) == False:
        print('ggg')
    

if __name__ == "__main__":
    main()

