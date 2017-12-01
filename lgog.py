#!/usr/bin/env python3
import os
import sys

import lgog.helper.lgogdownloader as lgogdownloader
import lgog.helper.log as log
from lgog.helper import user
from lgog.download_directory import DownloadDir
from lgog.game_data import GameData
from lgog.helper.config import parse_config
from lgog.helper.command_line import parse_command_line
from lgog.helper.local import check_files
from lgog.helper.log import logger


def main(args):
    """
    Run main program.

    :param args: Parsed command line arguments.
    """
    logger.debug(f"Running with args: {args}")

    game_data = GameData(DATA_PATH)

    # Automatically run update if game_data is outdated
    if args.update or game_data.is_outdated:
        lgogdownloader.update_cache()

    if args.directory:
        directory = os.path.abspath(args.directory)
    else:
        # Get directory from lgog config by default
        directory = parse_config(CONFIG_PATH, "directory")

    download_directory = DownloadDir(directory)
    games_with_update = check_files(game_data, download_directory)

    if args.clean:
        print("Cleaning outdated setup files...")
        for game in games_with_update:
            download_directory.delete_files(game)
        print("Done.")
        sys.exit()

    if not args.all:
        # Ask for download confirmation by default
        for game in games_with_update:
            if game.conf:
                continue

            # Unselect game if user reponse is "no"
            prompt = f"Re-download file(s) for {game.name}?"
            if not user.confirm(prompt):
                game.update = False
                game.conf = True

    # Download files for every selected game
    download_games = [g for g in games_with_update if g.update]
    for game in download_games:
        game.update_game()

    if args.delete:
        prompt = "\nDelete old setup files?"
        if user.confirm(prompt):
            print("Deleting files...")
            for game in download_games:
                    download_directory.delete_files(game)

    print("Done.")


if __name__ == "__main__":

    HOME = os.getenv("HOME")
    DATA_PATH = os.path.join(HOME, ".cache/lgogdownloader/gamedetails.json")
    CONFIG_PATH = os.path.join(HOME, ".config/lgogdownloader/config.cfg")

    args = parse_command_line()

    if args.debug:
        logging_level = log.levels.get(args.debug)
        log.console.setLevel(logging_level)

    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        logger.info("Aborted by user (ctrl+c)")
