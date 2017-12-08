"""Functions that make direct use of lgogdownloader"""

from lgog.helper import run


def update_cache():
    """Update gamedetails.json"""
    args = ["lgogdownloader", "--update-cache"]

    print("Updating game data...")
    run_lgogdownloader(args)
    print("Completed update\n")


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
    run_lgogdownloader(args)
    print("Download complete\n")


def run_lgogdownloader(args):
    """Run lgogdownloader as if it were executed from the command line.

    :param args: List of arguments to be passed to lgogdownloader
    """
    run.command(args)
