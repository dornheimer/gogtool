#!/usr/bin/env python3
import os
import sys

import lgog.helper.lgogdownloader as lgogdownloader
import lgog.helper.log as log
from lgog.download_directory import DownloadDir
from lgog.installation_directory import InstallDir
from lgog.library_data import LibraryData
from lgog.local_library import LocalLibrary
from lgog.helper.config import parse_config
from lgog.helper.command_line import parse_command_line
from lgog.helper.log import logger


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
        directory = os.path.abspath(args.directory)
    else:
        # Get directory from lgog config by default
        directory = parse_config(CONFIG_PATH, "directory")

    download_dir = DownloadDir(directory)
    download_dir.scan_for_setup_files(library_data.games)

    install_dir = InstallDir(INSTALL_PATH)

    local_library = LocalLibrary(library_data, download_dir, install_dir)

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
    INSTALL_PATH = HOME

    args = parse_command_line()

    if args.debug:
        logging_level = log.levels.get(args.debug)
        log.console.setLevel(logging_level)

    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        logger.info("Aborted by user (ctrl+c)")
