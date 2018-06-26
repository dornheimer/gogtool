import argparse
import sys

import yaml

from gogtool.main import initialize_gogtool, run_gogtool


parser = argparse.ArgumentParser(
    prog='gogtool',
    description="a small extension for lgogdownloader",
)

parser.add_argument(
    '--list',
    choices=['downloaded', 'installed', 'all', 'outdated'],
    help="list all games in category (default platform='l')"
)
parser.add_argument(
    '--platform',
    choices=['l', 'w'],
    default='l',
    help="""
        set platform
        valid options are: l (linux), w (windows)
        """,
    metavar="",
)
parser.add_argument(
    '--show-files',
    action='store_true',
    dest='files',
    help="show additional file information in list"
)
parser.add_argument(
    '--update',
    metavar='<game>',
    help="download and install newest version of game(s)"
)
parser.add_argument(
    '--info',
    action='store_true',
    help="show general library information"
)
parser.add_argument(
    '--download',
    nargs='+',
    metavar='<game>',
    help="download game(s)"
)
parser.add_argument(
    '--install',
    nargs='+',
    metavar='<game>',
    help="install game(s). if necessary, downloads setup files."
)
parser.add_argument(
    '--uninstall',
    nargs='+',
    metavar='<game>',
    help="uninstall game(s)"
)
parser.add_argument(
    '--remove',
    nargs='+',
    metavar='<game>',
    help="delete setupfile for game(s)"
)
parser.add_argument(
    '--clean',
    action='store_true',
    help="delete orphaned setup files"
)
parser.add_argument(
    '--refresh',
    action='store_true',
    help="update lgogdownloader's library cache"
)
parser.add_argument(
    '--view',
    help="browse install directory of a game",
    metavar='<game>'
)
parser.add_argument(
    '--edit-lgogconfig',
    action='store_true',
    help="open lgogdownloader's config in the default text editor"
)
parser.add_argument(
    '--debug',
    choices=['info', 'debug', 'warning', 'critical', 'error', 'notset'],
    nargs='?',
    const='debug',
    default='warning',
    help="""
        show debug information.
        valid options are: info, debug, warning, critical, error, notset
        """,
    metavar="",
)
parser.add_argument(
    '--launch',
    metavar='<game>',
    help="start a game"
)


def load_config(config_file):
    with open(config_file) as f:
        return yaml.load(f)


def main():
    args = parser.parse_args()
    config, library = initialize_gogtool(args)

    try:
        return run_gogtool(config, library, args, cli=True)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    sys.exit(main())
