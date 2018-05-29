import argparse
import json
import os
import sys

import yaml

from gogtool import lgog, util
from gogtool.config import configure_gogtool
from gogtool.info import (print_all, print_downloaded, print_installed,
                          print_outdated, print_stats)
from gogtool.library import Library
from gogtool.log import configure_logger


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--list',
        choices=['downloaded', 'installed', 'all', 'outdated']
    )
    parser.add_argument('--platform', choices=['l', 'w'], default='l')
    parser.add_argument('--show-files', action='store_true', dest='files')
    parser.add_argument('--update')
    parser.add_argument('--info', action='store_true')
    parser.add_argument('--download', nargs='+')
    parser.add_argument('--dlc', action='store_true')
    parser.add_argument('--install', nargs='+')
    parser.add_argument('--uninstall', nargs='+')
    parser.add_argument('--remove', nargs='+')
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--view')
    parser.add_argument('--edit-lgogconfig', action='store_true')
    parser.add_argument(
        '--debug',
        choices=['info', 'debug', 'warning', 'critical', 'error', 'notset'],
        nargs='?',
        const='debug',
        default='warning'
    )

    return parser.parse_args()


def load_json(filepath):
    with open(filepath) as fp:
        return json.load(fp)


def load_config(config_file):
    with open(config_file) as f:
        return yaml.load(f)


def main(args):
    config = configure_gogtool()
    gog_library = load_json(config['lgog_data_path'])

    if Library.is_outdated(gog_library) or args.refresh:
        print("Library data is outdated. Updating...")
        lgog.run('--update-cache')
        gog_library = load_json(config['lgog_data_path'])

    library = Library(gog_library, config)

    if args.download:
        dest = config['download_dir']
        if len(args.download) == 1:
            game_name = args.download[0]
            lgog.download(game_name, dest)
        else:
            for game_name in args.download:
                lgog.download(game_name, dest)

    if args.install:
        if len(args.install) == 1:
            game_name = args.install[0]
            library.install(game_name)
        else:
            for game_name in args.install:
                library.install(game_name)

    if args.update:
        game_name = args.update
        installers = library.update(game_name)
        print(installers)

    if args.uninstall:
        if len(args.uninstall) == 1:
            game_name = args.uninstall[0]
            library.uninstall(game_name)
        else:
            for game_name in args.uninstall:
                library.uninstall(game_name)

    if args.remove:
        if len(args.remove) == 1:
            game_name = args.remove[0]
            library.delete_setup_files(game_name)
        else:
            for game_name in args.remove:
                library.delete_setup_files(game_name)

    if args.clean:
        library.delete_orphaned_files()

    if args.list:
        linux_only = (args.platform == 'l')
        if args.list == 'all':
            print_all(library, linux_only=linux_only)
        elif args.list == 'installed':
            print_installed(library, linux_only=linux_only)
        elif args.list == 'downloaded':
            print_downloaded(library, show_files=args.files, linux_only=linux_only)
        elif args.list == 'outdated':
            print_outdated(library, show_files=args.files, linux_only=linux_only)

    if args.view:
        library.view_install_dir(game_name=args.view)

    if args.info:
        print_stats(library)

    if args.edit_lgogconfig:
        config_path = config['lgog_config_path']
        util.run_command(['xdg-open', config_path])


if __name__ == '__main__':
    args = parse_commandline()

    log_level = args.debug
    log_file = os.path.join(os.getcwd(), 'gogtool.log')
    logger = configure_logger(log_level, log_file)

    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        logger.info("Aborted by user (ctrl+c)")
