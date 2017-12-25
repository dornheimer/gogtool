"""CLI for main application."""

import argparse


def parse_command_line():
    parser = argparse.ArgumentParser(prog="gogtool")
    #subparsers = parser.add_subparsers()

    #parser_list = subparsers.add_parser("list", help="show games of category")
    parser.add_argument("--list-installed", action="store_true",
                        dest="list_installed",
                        help="list installed games")
    parser.add_argument("--list-downloaded", action="store_true",
                        dest="list_downloaded",
                        help="list downloaded games")
    parser.add_argument("--list-outdated", action="store_true",
                        dest="list_outdated",
                        help="list only games with outdated installers")
    parser.add_argument("--list-all", action="store_true", dest="list_all",
                        help="list games in every category")
    parser.add_argument("--download-all", action="store_true",
                        help="download newer versions for all games found in download directory")
    parser.add_argument("--refresh-cache", action="store_true", dest="refresh",
                        help="refresh game details cache")
    parser.add_argument("--update-games", action="store_true",
                        help="initialize update for all outdated games")
    parser.add_argument("--delete", action="store_true",
                        help="delete outdated setup files after downloading newer versions")
    parser.add_argument("--log", nargs="?", const="gogtool.log",
                        help="save output to log file (default='gogtool.log')")
    parser.add_argument("--debug", nargs="?", const="debug", metavar="logging.LEVEL",
                        choices=["info", "debug", "warning", "critical", "error", "notset"],
                        help="""set logger level for console (default=INFO).
                        if argument is omitted, level is set to 'debug'""")
    parser.add_argument("--platform", nargs="+", choices={'1', '2', '4'}, default={'4', '1'},
                        help="set platform priority (default 1. 4=linux, 2. 1=windows)")
    parser.add_argument("--directory", metavar="path",
                        help="override default directory")
    parser.add_argument("--install", nargs="+",
                        help="install a game or a list of games")
    parser.add_argument("--download", nargs="+",
                        help="download a game or a list of games")
    parser.add_argument("--uninstall", nargs="+",
                        help="uninstall a game or a list of games")
    parser.add_argument("--clean", action="store_true",
                        help="delete old setup files if an up-to-date version is present")
    parser.add_argument("--info", action="store_true",
                        help="print general library information")

    return parser.parse_args()
