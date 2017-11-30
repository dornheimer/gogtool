import subprocess

from lgog.helper.log import logger


def update_cache():
    args = ["lgogdownloader", "--update-cache"]

    print("Updating game data...")
    run_command(args)
    print("Completed update")


def download(game, file_id=None):
    platform = "l" if game.platform == 4 else "w"
    args = ["lgogdownloader"]

    if file_id is not None:
        # Format: 'gamename/file_id'
        args.extend(["download-file", f"{game}/{file_id}"])
    else:
        args.extend(["--platform", platform, "--download", "--game", game])

    print(f"Downloading file(s) for {game}...")
    run_command(args)
    print("Download complete")


def run_command(args):
    args_str = ', '.join(args)
    logger.debug(f"Executing '{args_str}'...")
    lgog = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdout = lgog.communicate()[0]

    rc = lgog.returncode
    if rc != 0:
        logger.error(f"lgogdownloader exited with error (return code: {rc})")
