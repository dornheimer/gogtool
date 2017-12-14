"""Functions for performing tasks on the OS level."""

import os
import shutil
import sys

from gogtool.helper.log import logger


def mkdir(directory):
    """Recursively create a directory."""
    try:
        os.makedirs(directory)
    except OSError:
        logger.error(f"Directory {directory} already exists")
        sys.exit(2)
    else:
        logger.debug(f"Sucessfully created {directory}")


def move(src, dest):
    shutil.move(src, dest)


def rmdir(path):
    """Remove file or directory."""
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        logger.error(f"{path} does not exist.")
        sys.exit(2)
    else:
        logger.debug(f"Sucessfully deleted {path}")


def rm(file):
    try:
        if os.path.exists(file):
            os.remove(file)
    except FileNotFoundError:
        logger.error("File path does not exist", exc_info=True)
    else:
        logger.debug(f"Removed '{file}'")
        print(file)
