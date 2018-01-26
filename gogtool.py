#!/usr/bin/env python3
import os
import sys

import gogtool.helper.lgogdownloader as lgogdownloader
import gogtool.helper.log as log
from gogtool.library_data import LibraryData
from gogtool.local_library import LocalLibrary
from gogtool.helper.config import parse_config
from gogtool.helper.command_line import parse_command_line
from gogtool.helper.log import logger


def main(args):
    """
    Run main program.

    :param args: Parsed command line arguments.
    """
    logger.debug(f"Running with args: {args}")

    library_data = LibraryData(DATA_PATH)

    # Automatically run update if library_data is outdated
    if args.refresh or library_data.is_outdated:
        lgogdownloader.update_cache()

    if args.directory:
        DOWNLOAD_PATH = os.path.abspath(args.directory)
    else:
        # Get directory from lgog config by default
        DOWNLOAD_PATH = parse_config(CONFIG_PATH, "directory")

    local_library = LocalLibrary(library_data, DOWNLOAD_PATH, INSTALL_PATH)

    if args.download:
        delete_old = args.delete
        download_queue = args.download
        logger.info(f"Downloading: {', '.join(download_queue)}")
        for game_name in download_queue:
            local_library.download_game(game_name, delete_old)
        sys.exit()

    if args.install:
        install_queue = args.install
        logger.info(f"Installing: {', '.join(install_queue)}")
        for game_name in install_queue:
            local_library.install_game(game_name)
        sys.exit()

    if args.uninstall:
        uninstall_queue = args.uninstall
        logger.info(f"Uninstalling: {', '.join(uninstall_queue)}")
        for game_name in uninstall_queue:
            local_library.uninstall_game(game_name)
        sys.exit()

    if args.list_downloaded:
        local_library.print_list("downloaded")

    if args.list_installed:
        local_library.print_list("installed")

    if args.list_outdated:
        local_library.print_list("outdated")

    if args.list_all:
        local_library.print_list("downloaded")
        local_library.print_list("installed")
        local_library.print_list("outdated")

    if args.info:
        local_library.print_info()

    if args.clean:
        local_library.clean()
        sys.exit()

    if args.update_games:
        download_all = args.download_all
        delete_by_default = args.delete
        local_library.update_games(download_all, delete_by_default)

    if local_library.download_queue:
        for game in local_library.download_queue:
            local_library.download_game(game.name)


if __name__ == "__main__":

    HOME = os.getenv("HOME")
    DATA_PATH = os.path.join(HOME, ".cache/lgogdownloader/gamedetails.json")
    CONFIG_PATH = os.path.join(HOME, ".config/lgogdownloader/config.cfg")
    INSTALL_PATH = os.path.join(HOME, "GOG Games/")

    args = parse_command_line()

    if args.debug:
        logging_level = log.levels.get(args.debug)
        log.console.setLevel(logging_level)

    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        logger.info("Aborted by user (ctrl+c)")
