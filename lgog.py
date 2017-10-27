import argparse
import json
import os
import subprocess
import sys

# FUNCTIONS: UPDATE, CLEAN, (logfile, verbose, platform, download_directory, delete_files, )


def check_input(prompt, choices={'y', 'n'}):
    """Verify user input."""
    while True:
        choice = input(prompt)
        if choice in choices:
            break
        print(f'Invalid option: {choice}')

    return choice


def delete_files(download_directory, game, filenames):
    """Delete all files in <filenames>."""
    for fn in filenames:
        file_path = os.path.join(download_directory, game, fn)
        print(file_path)
        os.remove(file_path)


def get_installer_info(game_name, game_details, platforms={4, 1}, id_prefix='en'):
    """Get installer info for <game_name> from game details."""
    for game in game_details['games']:
        if game['gamename'] == game_name:

            installers = {}
            for inst in game['installers']:
                if inst['platform'] in platforms and inst['id'].startswith(id_prefix):
                    installers.setdefault(inst['platform'], []).append(inst['path'])

    return installers


def parse_command_line():
    """Get args from command line."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.add_argument("--all", action="store_true",
                        help="download newer versions for all games found in default directory")
    parser.add_argument("--update", action="store_true", help="update game details cache")
    parser.add_argument("--delete", action="store_true", help="delete outdated setup files after update")
    parser.add_argument("--list", action="store_true", help="list outdated setup files")
    parser.add_argument("--log", nargs="?", type=argparse.FileType('w'), default=sys.stdout,
                        help="save output to log file")
    parser.add_argument("--verbose", action="store_true", help="print more information")
    parser.add_argument("--platform", nargs="+", choices={'1', '2', '4'}, default={'4', '1'},
                        help="set platform priority (default 1. 4=linux, 2. 1=windows)")
    parser.add_argument("--directory", nargs="+", help="override default directory")
    parser.add_argument("--clean", action="store_true", help="delete orphaned setup files")

    return parser.parse_args()


def parse_config(path, key=None):
    """Return dictionary with options -> values from lgog config file."""
    with open(path, 'r') as config_file:
        lines = config_file.readlines()
        config_dict = dict(line.strip().split(" = ") for line in lines)

    if key:
        return config_dict[key]

    return config_dict


def main():
    # get args from command line
    args = parse_command_line()

    # get download directory from lgog config
    config_path = os.path.join(HOME, '.config/lgogdownloader/config.cfg')
    download_directory = parse_config(config_path, 'directory')
    print(f'Download directory is: {download_directory}')

    # get list of folders in download directory (folder names are game names)
    games = os.listdir(download_directory)

    # update game details cache
    if args.update:
        print("Running 'lgogdownloader --update-cache'...")
        update_cache = subprocess.Popen(["lgogdownloader", "--update-cache"], stdout=subprocess.PIPE)
        stdout, _ = update_cache.communicate()

    # get game details from json file
    data_path = os.path.join(HOME, ".cache/lgogdownloader/gamedetails.json")
    with open(data_path) as data:
        game_details = json.load(data)

    # check if local file names match those on the server
    update = []
    print("\nChecking local files...")
    for game in games:
        file_names = os.listdir(os.path.join(download_directory, game))
        local_files = [fn for fn in file_names if fn.startswith(('gog', 'setup', game))]

        # prefer linux installer (compare win files otherwise)
        if get_installer_info(game, game_details).get(4):
            server_path = get_installer_info(game, game_details)[4]
            platform = 'linux'

        else:
            server_path = get_installer_info(game, game_details)[1]
            platform = 'windows'

        server_files = [os.path.basename(sp) for sp in server_path]

        if all([(sf in local_files) for sf in server_files]):
            if args.verbose:
                print(f'\n{game} is up-to-date.')
        else:
            if args.verbose:
                print(f'\nFiles for {game} do not match:')
                print("local: " + ", ".join(local_files))
                print("server: " + ", ".join(server_files))

            update.append((game, platform, local_files))

    print("\nGames with outdated setup files:")
    print("\n".join([g for g, p, lf in update]), end="\n\n")

    if args.clean:
        print("Cleaning outdated setup files...")
        for g, p, lf in update:
            delete_files(download_directory, g, lf)
        sys.exit('Done.')

    if args.all:
        for i, g in enumerate(update):
            update[i] = (g, 'y')
    else:
        for i, g in enumerate(update):
            choice = check_input(f'Re-download file(s) for {g[0]}? (y/n) ')
            update[i] = (g, choice)

    for (g, p, lf), c in update:
        if c == 'y':
            if p == 'windows':
                update_args = ["lgogdownloader", "--platform", "w", "--download", "--game", f"{g}"]
            else:
                update_args = ["lgogdownloader", "--download", "--game", f"{g}"]
            print(f'Downloading file(s) for {g}...')
            update_files = subprocess.Popen(update_args, stdout=subprocess.PIPE)
            stdout, _ = update_files.communicate()
            out = stdout.decode('utf-8')

    if args.delete:
        delete_conf = check_input("\nDelete old setup files? (y/n) ")
        if delete_conf == 'y':
            print("Deleting files...")
            for (g, p, lf), c in update:
                if c == 'y':
                    delete_files(download_directory, g, lf)

    print('\nDone.')


if __name__ == '__main__':

    HOME = os.environ['HOME']
    sys.exit(main())
