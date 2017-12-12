"""Execute process."""

import subprocess

from gogtool.helper.log import logger


def command(args):
    """Run process as if it were executed from the command line.

    :param args: List of command line arguments
    """
    args_str = ', '.join(args)
    logger.debug(f"Executing '{args_str}'...")
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if logger.getEffectiveLevel() == 10:
        print(stdout.decode())

    rc = process.returncode
    if rc != 0:
        logger.warning(f"{args[0]} exited with error (return code: {rc})")

    return rc
