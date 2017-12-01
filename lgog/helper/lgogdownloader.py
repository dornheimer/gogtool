"""Functions that make direct use of lgogdownloader"""

import subprocess

from lgog.helper.log import logger


def update_cache():
    """Update gamedetails.json"""
    args = ["lgogdownloader", "--update-cache"]

    print("Updating game data...")
    run_command(args)
    print("Completed update")


def download(game_name, platform, file_id=None):
    """Download game installers from GOG server by either name or file ID.

    :param game: A Game object
    :param file_id: ID of file on the server
    """
    # Convert numeric identifier to string
    platform = "l" if platform == 4 else "w"
    args = ["lgogdownloader"]

    if file_id is not None:
        # Format: 'gamename/file_id'
        args.extend(["download-file", f"{game_name}/{file_id}"])
    else:
        args.extend(["--platform", platform, "--download", "--game", game_name])

    print(f"Downloading file(s) for {game_name}...")
    run_command(args)
    print("Download complete")


def run_command(args):
    """Run lgogdownloader as if it were executed from the command line.

    :param args: List of arguments to be passed to lgogdownloader
    """
    args_str = ', '.join(args)
    logger.debug(f"Executing '{args_str}'...")
    lgog = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdout = lgog.communicate()[0]

    rc = lgog.returncode
    if rc != 0:
        logger.error(f"lgogdownloader exited with error (return code: {rc})")
