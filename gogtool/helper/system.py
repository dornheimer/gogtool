"""Functions for performing tasks on the OS level."""

import os
import shutil
import sys

from gogtool.helper.log import logger


def mkdir(directory):
    """Recursively create a directory."""
    try:
        os.makedirs(directory, exist_ok=True)
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


def rm(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except FileNotFoundError:
        logger.error("File path does not exist", exc_info=True)
    else:
        logger.debug(f"Removed '{file_path}'")


def update_dir(src, dst):
    """Copy files from src to dst.

    If a file already exists in the destination directory, remove it before
    copying the file from source.
    """
    logger.debug("Updating installation with extracted files...")
    for src_dir, subdirectory, files in os.walk(src):
        dst_dir = src_dir.replace(src, dst, 1)  # Equivalent of src in dst
        if not os.path.exists(dst_dir):
            mkdir(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):  # Remove file if it exists
                rm(dst_file)
            move(src_file, dst_dir)
