"""Functions for performing tasks on the OS level."""

import os
import shutil
import sys

from lgog.helper.log import logger


def mkdir(directory):
    """Recursively create directory."""
    try:
        os.makedirs(directory)
    except OSError:
        logger.error(f"Directory {directory} already exists")
        sys.exit(2)
    else:
        logger.debug(f"Sucessfully created {directory}")


def move(src, dest):
    shutil.move(src, dest)


def rm(path):
    """Remove file or directory."""
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        logger.error(f"{path} does not exist.")
        sys.exit(2)
    else:
        logger.debug(f"Sucessfully created {path}")
