"""CLI for main application."""

import argparse


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
    parser.add_argument("--clean", action="store_true",
                        help="delete orphaned setup files")

    return parser.parse_args()
