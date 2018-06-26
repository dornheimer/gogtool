import os

from gogtool import lgog, util
from gogtool.config import configure_gogtool
from gogtool.info import (print_all, print_downloaded, print_installed,
                          print_outdated, print_stats)
from gogtool.library import Library
from gogtool.log import configure_logger


def initialize_gogtool(args):
    log_level = args.debug
    log_file = os.path.join(os.getcwd(), 'gogtool.log')
    configure_logger(log_level, log_file)

    config = configure_gogtool()
    library = initialize_library(args, config, log_level=log_level)

    return config, library


def initialize_library(args, config, log_level='warning'):
    gog_library = util.load_json(config['lgog_data_path'])
    if not any([args.download, args.launch, args.edit_lgogconfig, args.view]):
        if Library.is_outdated(gog_library) or args.refresh:
            print("Updating library data...")
            lgog.run('--update-cache')
            gog_library = util.load_json(config['lgog_data_path'])

    return Library(gog_library, config)


def get_games(library, category, linux_only):
    game_categories = {
        'all': library.all_games,
        'downloaded': library.downloaded_games,
        'installed': library.installed_games,
        'outdated': library.outdated_games,
    }
    games = game_categories[category]
    if linux_only:
        games = [g for g in games if g.linux_available]
    return games


def get_print_func(category):
    print_funcs = {
        'all': print_all,
        'downloaded': print_downloaded,
        'installed': print_installed,
        'outdated': print_outdated
    }
    return print_funcs[category]


def run_gogtool(config, library, args, cli=False):
    if args.download:
        if len(args.download) == 1:
            game_name = args.download[0]
            library.download(game_name)
        else:
            for game_name in args.download:
                library.download(game_name)

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
        games_category = args.list
        linux_only = (args.platform == 'l')
        games = get_games(library, games_category, linux_only=linux_only)
        if cli:
            print_func = get_print_func(games_category)
            print_func(library)
        else:
            return games

    if args.view:
        library.view_install_dir(game_name=args.view)

    if args.info:
        if cli:
            print_stats(library)
        else:
            num_games_library = len(library.gog_games)
            num_games_downloaded = len(library.downloaded_games)
            num_games_installed = len(library.installed_games)
            return num_games_library, num_games_downloaded, num_games_installed

    if args.edit_lgogconfig:
        config_path = config['lgog_config_path']
        util.run_command(['xdg-open', config_path])

    if args.launch:
        library.run(game_name=args.launch)
