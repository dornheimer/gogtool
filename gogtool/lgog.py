import logging

from gogtool.util import run_command

logger = logging.getLogger(__name__)


def run(command_string):
    command_args = command_string.split()
    run_command(['lgogdownloader'] + command_args)


def download(game_name, dest):
    print(f"Downloading {game_name}...")
    run(f"--download --directory {dest} --game {game_name }")
