"""Execute process."""

import subprocess

from gogtool.helper.log import logger


def command(args, shell=False):
    """Run process as if it were executed from the command line.

    :param args: List of command line arguments.
    """
    args_str = ' '.join(args)
    logger.debug(f"Executing '{args_str}'...")
    if shell:
        # Escape spaces if arg is a path
        shell_args = " ".join([arg.replace(" ", "\ ") for arg in args])
        process = subprocess.Popen(shell_args, shell=True)
    else:
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

    if logger.getEffectiveLevel() == 10:
        stdout, stderr = process.communicate()
    # if logger.getEffectiveLevel() == 10:
    #     print(stdout.decode())

    rc = process.returncode
    if rc != 0:
        logger.warning(f"{args[0]} exited with error (return code: {rc})")

    return rc
