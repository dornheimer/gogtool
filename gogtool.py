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
    if args.update or library_data.is_outdated:
        lgogdownloader.update_cache()

    if args.directory:
        DOWNLOAD_PATH = os.path.abspath(args.directory)
    else:
        # Get directory from lgog config by default
        DOWNLOAD_PATH = parse_config(CONFIG_PATH, "directory")

    local_library = LocalLibrary(library_data, DOWNLOAD_PATH, INSTALL_PATH)

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

    if args.clean:
        print("Cleaning outdated setup files...")
        for game in local_library.games_with_update:
            download_dir.delete_files(game)
        print("Done.")
        sys.exit()

    download_all = args.all
    delete_by_default = args.delete
    local_library.update_games(download_all, delete_by_default)

    print("Done.")


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
