import os
from colorama import Fore, Style, init

init(autoreset=True)

dim = lambda string: Style.DIM + string
fblue = lambda string: Fore.BLUE + string
fcyan = lambda string: Fore.CYAN + string
fgreen = lambda string: Fore.GREEN + string
fred = lambda string: Fore.RED + string
fblue = lambda string: Fore.BLUE + string
fyellow = lambda string: Fore.YELLOW + string
freset = lambda string: Fore.RESET + string


def wrap_line(string, width=25):
    if len(string) > width:
        return string[:width], string[width:][:width]
    return string


def print_stats(library):
    print("{} games in GOG library".format(len(library.gog_games)))
    print("{} downloaded".format(len(library.downloaded_games)))
    print("{} installed".format(len(library.installed_games)))


def print_files(game):
    if game.is_downloaded:
        downloaded_files = [os.path.basename(df) for df in game.downloaded_files]
        if game.needs_update:
            downloaded_fmt = fred("\n".join(downloaded_files))
        else:
            downloaded_fmt = fgreen("\n".join(downloaded_files))
        print(dim(f"{'downloaded':<10} : {downloaded_fmt}"))

    if not game.is_downloaded or game.needs_update:
        available_fmt = fcyan("\n".join(game.match_downloaded(basename=True)))
        print(dim(f"{'available':<10} : {available_fmt}"))
    print()


def print_downloaded(library, show_files=False, linux_only=True):
    for game in library.downloaded_games:
        if linux_only and not game.linux_available:
            continue
        needs_update = fred('needs update') if game.needs_update else fgreen('latest')
        installed = fblue('installed') if game.is_installed else dim(freset('not installed'))
        name_wrapped = wrap_line(game.name)
        if len(name_wrapped) == 2:
            print(f"{name_wrapped[0]:<25} :: {needs_update:<17} {installed}")
            print(f"{name_wrapped[1]:<25}")
        else:
            print(f"{name_wrapped:<25} :: {needs_update:<17} {installed}")

        if show_files:
            print_files(game)


def print_installed(library, linux_only=True):
    for game in library.installed_games:
        if linux_only and not game.linux_available:
            continue
        needs_update = fred('needs update') if game.needs_update else fgreen('latest')
        name_wrapped = wrap_line(game.name)
        if game.is_downloaded:
            if len(name_wrapped) == 2:
                print(f"{name_wrapped[0]:<25} :: {needs_update:<17}")
                print(f"{name_wrapped[1]:<25}")
            else:
                print(f"{name_wrapped:<25} :: {needs_update:<17}")
        else:
            print(f"{name_wrapped:<25} :: {fblue('installed'):<17}")
        if game.has_dlc and game.dlc_installed:
            for dlc in game.installable_dlcs:
                print(dlc)


def print_outdated(library, show_files=False, linux_only=True):
    for game in library.outdated_games:
        if linux_only and not game.linux_available:
            continue
        installed = fblue('installed') if game.is_installed else dim(freset('not installed'))
        name_wrapped = wrap_line(game.name)
        if len(name_wrapped) == 2:
            print(f"{name_wrapped[0]:<25} :: {installed}")
            print(f"{name_wrapped[1]:<25}")
        else:
            print(f"{name_wrapped:<25} :: {installed}")

        if show_files:
            print_files(game)


def print_all(library, linux_only=True):
    for game in library.gog_games:
        g = library.get_game(game['gamename'])
        if linux_only and not g.linux_available:
            continue
        print(g)
