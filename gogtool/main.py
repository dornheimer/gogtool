from gogtool import util
from gogtool.info import (print_all, print_downloaded, print_installed,
                          print_outdated, print_stats)


def run_gogtool(config, library, args):

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

    if args.launch:
        library.run(game_name=args.launch)
