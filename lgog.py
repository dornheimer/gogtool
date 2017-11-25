import argparse
import logging
import json
import os
import subprocess
import sys


from download_directory import DownloadDir
from game import Game

# FUNCTIONS: UPDATE, CLEAN, (logfile, verbose, platform, download_directory, delete_files, )


def check_input(prompt, choices={'y', 'n'}):
    """Verify user input."""
    while True:
        choice = input(prompt)
        if choice in choices:
            break
        print(f'Invalid option: {choice}')

    return choice


def get_games_data(data_path):
    """Get game details from lgogdownloader json file."""
    try:
        with open(data_path) as data:
            games_data = json.load(data)["games"]
    except FileNotFoundError:
        logger.error(f"Game details data not found in {data_path}", exc_info=True)
        sys.exit()

    logger.debug(f"Game details data found in {data_path}")
    return games_data


def get_game_info(game, games_data):
    for title in games_data:
        if title['gamename'] == game:

            return title


# def check_for_update(games, games_data, download_dir, verbose=False):
#     """Check if local file names match those on the server."""
#     update = []
#     print("\nChecking local files...")
#     for game in games:
#         file_names = os.listdir(os.path.join(download_dir, game))
#         local_files = [fn for fn in file_names if fn.startswith(('gog', 'setup', game))]
#
#         # prefer linux installer (compare win files otherwise)
#         if get_installer_info(game, games_data).get(4):
#             server_path = get_installer_info(game, games_data)[4]
#             platform = 'linux'
#         else:
#             server_path = get_installer_info(game, games_data)[1]
#             platform = 'windows'
#
#         server_files = [os.path.basename(sp) for sp in server_path]
#
#         if all([(sf in local_files) for sf in server_files]):
#             if verbose:
#                 print(f'\n{game} is up-to-date.')
#         else:
#             if verbose:
#                 print(f'\nFiles for {game} do not match:')
#                 print("local: " + ", ".join(local_files))
#                 print("server: " + ", ".join(server_files))
#
#             update.append((game, platform, local_files))
#
#         return update


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true",
                        help="download newer versions for all games found in default directory")
    parser.add_argument("--update", action="store_true",
                        help="update game details cache")
    parser.add_argument("--delete", action="store_true",
                        help="delete outdated setup files after update")
    parser.add_argument("--list", action="store_true",
                        help="list outdated setup files")
    # parser.add_argument("--log", nargs="?", type=argparse.FileType('w'), default=sys.stdout,
    #                     help="save output to log file")
    parser.add_argument("--verbose", action="store_true",
                        help="print more information")
    parser.add_argument("--platform", nargs="+", choices={'1', '2', '4'}, default={'4', '1'},
                        help="set platform priority (default 1. 4=linux, 2. 1=windows)")
    parser.add_argument("--directory", nargs="+",
                        help="override default directory")
    parser.add_argument("--clean", action="store_true",
                        help="delete orphaned setup files")

    args = parser.parse_args()
    logger.debug(f"Running with args: {args}")

    return args


def parse_config(path, key=None):
    """Return dictionary with options -> values from lgog config file."""
    with open(path, 'r') as config_file:
        lines = config_file.readlines()
        config_dict = dict(line.strip().split(" = ") for line in lines)
    if key:
        try:
            key_value = config_dict[key]
            logger.debug(f"Succesfully parsed config file with key: '{key}'")
            return key_value
        except KeyError:
            logger.error(f"Invalid key: '{key}'", exc_info=True)

    logger.debug("Succesfully parsed config file.")
    return config_dict


def main():
    # get args from command line
    args = parse_command_line()

    # update game details cache
    if args.update:
        logger.info("Running 'lgogdownloader --update-cache'...")
        update_cache = subprocess.Popen(["lgogdownloader", "--update-cache"], stdout=subprocess.PIPE)
        stdout, _ = update_cache.communicate()
        sys.exit(logger.info("Completed update."))

    # get download directory from lgog config
    games_data = get_games_data(DATA_PATH)

    download_directory = DownloadDir(parse_config(CONFIG_PATH, 'directory'))
    logger.info(f'Download directory is: {download_directory.path}')

    local_games = []
    for game in download_directory.games:
        local_games.append(Game(game,
                                get_game_info(game, games_data),
                                download_directory.files[game]["local_path"]))

    # check every game and add to list if an update is available
    update = [lg for lg in local_games if lg.check_for_update()]
    print("\nGames with outdated setup files:")
    print("\n".join([g.name for g in update]), end="\n\n")

    if args.clean:
        print("Cleaning outdated setup files...")
        for game in update:
            download_directory.delete_files(game)
        print("Done.")
        sys.exit()

    if not args.all:
        # ask for download confirmation by default
        for game in update:
            choice = check_input(f'Re-download file(s) for {game.name}? (y/n) ')
            if choice == "n":
                game.update = False

    # download files for every selected game
    for game in update:
        game.download()

    if args.delete:
        delete_conf = check_input("\nDelete old setup files? (y/n) ")
        if delete_conf == 'y':
            print("Deleting files...")
            for game in update:
                download_directory.delete_files(game)

    print('Done.')


if __name__ == '__main__':

    HOME = os.environ['HOME']
    DATA_PATH = os.path.join(HOME, ".cache/lgogdownloader/gamedetails.json")
    CONFIG_PATH = os.path.join(HOME, '.config/lgogdownloader/config.cfg')

    logging.basicConfig(format="%(name)s:%(levelname)s: %(message)s", level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logging.info("Aborted by user.")
