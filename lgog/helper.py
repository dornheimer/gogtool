import argparse
import logging

from lgog.game import Game


logger = logging.getLogger("__main__")


def check_input(prompt, choices={'y', 'n'}):
    """Verify user input."""
    while True:
        choice = input(prompt)
        if choice.lower() in choices:
            break
        print(f'Invalid option: {choice}')

    return choice


def check_local_files(game_data, download_directory):
    """Check files of every game and add to list if an update is available."""
    local_games = []
    for game in download_directory.games:

        game_info = game_data.get_game_info(game)
        local_path = download_directory.files[game]["local_path"]
        local_files = download_directory.files[game]["setup_files"]
        game_object = Game(game, game_info, local_path, local_files)
        local_games.append(game_object)

        logger.debug(f"Local files for {game}: {len(local_files)}")
        if local_files == []:  # Empty folder
            prompt = (f"Folder for {game} is empty. Download latest installer? (y/n) ")
            if check_input(prompt) == "y":
                game_object.update = True
                game_object.conf = True

    games_with_update = [lg for lg in local_games if lg.check_for_update()]
    print("\nGames with outdated setup files:")
    print("\n".join([g.name for g in games_with_update]), end="\n\n")

    logger.debug(f"{len(games_with_update)} games with updates")
    return games_with_update


def parse_command_line():
    parser = argparse.ArgumentParser(prog="lgog")
    parser.add_argument("--all", action="store_true",
                        help="download newer versions for all games found in default directory")
    parser.add_argument("--update", action="store_true",
                        help="update game details cache")
    parser.add_argument("--delete", action="store_true",
                        help="delete outdated setup files after update")
    parser.add_argument("--list", action="store_true",
                        help="list outdated setup files")
    parser.add_argument("--log", nargs="?", const="lgog.log",
                        help="save output to log file (default='lgog.log')")
    parser.add_argument("--debug", nargs="?", default="warning", const="info",
                        choices=["info", "debug", "warning", "critical", "error", "notset"],
                        help="print more information")
    parser.add_argument("--platform", nargs="+", choices={'1', '2', '4'}, default={'4', '1'},
                        help="set platform priority (default 1. 4=linux, 2. 1=windows)")
    parser.add_argument("--directory", nargs="+",
                        help="override default directory")
    parser.add_argument("--clean", action="store_true",
                        help="delete orphaned setup files")

    return parser.parse_args()


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

    logger.debug("Succesfully parsed config file")
    return config_dict


def setup_logging(args):

    levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
            "notset": logging.NOTSET,
            }

    logging_level = levels.get(args.debug)

    if args.log is not None:
        # Set up logging to file
        config_kwargs = {
            "filename": args.log,
            "filemode": "w",
            "format": "%(asctime)s - %(levelname)s:%(name)s:[%(funcName)s]: %(message)s",
            "datefmt": "%H:%M:%S",
            "level": logging_level}
    else:
        # Log to console only
        config_kwargs = {
            "format": "%(levelname)s:%(name)s:[%(funcName)s]: %(message)s",
            "level": logging_level}

    logging.basicConfig(**config_kwargs)

    if args.log is not None:
        # Log to both console and file
        console = logging.StreamHandler()
        console.setLevel(logging_level)
        formatter = logging.Formatter("%(levelname)s:%(name)s:[%(funcName)s]: %(message)s")
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)

    logger = logging.getLogger(__name__)
    logger.debug(f"logger '{logger.name}' created")
    return logger
