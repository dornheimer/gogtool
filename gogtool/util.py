import logging
import os
import shutil
import subprocess
import tempfile

logger = logging.getLogger(__name__)


def move(src, dest):
    shutil.move(src, dest)


def rm(filepath):
    logger.debug("Removing file: %s", filepath)
    try:
        os.remove(filepath)
    except FileNotFoundError:
        log_msg = "File not found"
        logger.error("%s: %s", log_msg, filepath)
        print(log_msg)


def rm_all(files):
    for f in files:
        rm(f)


def rmdir(dirpath):
    logger.debug("Removing directory: %s", dirpath)
    shutil.rmtree(dirpath)


def mkdir(dirpath):
    logger.debug("Creating directory: %s", dirpath)
    os.makedirs(dirpath, exist_ok=True)


def update_dir(src, dest):
    logger.debug("Updating directory: %s (from %s)", dest, src)
    for src_dir, sub_dir, files in os.walk(src):
        dest_dir = src_dir.replace(src, dest, 1)  # Equivalent of src in dest
        if not os.path.exists(dest_dir):
            mkdir(dest_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dest_file = os.path.join(dest_dir, file_)
            if os.path.exists(dest_file):  # Remove file if it exists
                rm(dest_file)
            move(src_file, dest_dir)


def run_command(args, shell=False):
    logger.info("Running %s", " ".join(args))
    if shell:
        # Escape spaces if arg is a path
        shell_args = " ".join([arg.replace(" ", "\ ") for arg in args])
        process = subprocess.Popen(shell_args, shell=True)
        return
    else:
        process = subprocess.Popen(args, stdout=subprocess.PIPE)

    while True:
        output = process.stdout.readline()
        rc = process.poll()
        if output == b'' and rc is not None:
            break
        logger.debug(output.decode('utf-8').strip())
    return rc


def user_confirm(prompt, default=False):
    responses_true = ["y", "yes", "1", "true"]
    responses_false = ["n", "no", "0", "false"]
    valid_responses = responses_true + responses_false
    prompt += " (y/n) "

    res = verify_user_response(prompt, valid_responses)
    if res is not None:
        return (res in responses_true)

    return default


def verify_user_response(prompt, valid_reponses, attempts=3):
    for attempt in range(attempts):
        res = input(prompt).lower()
        if res in valid_reponses:
            return res
        print(f'Invalid option: {res}')

    print("No choice was made.")
    return None


def listdir(dirpath):
    return [os.path.join(dirpath, fp) for fp in os.listdir(dirpath)]


def open_dir(dirpath):
    run_command(['xdg-open', dirpath])


def extract_linux_installer(installer, dest):
    # Extract files into temp dir
    mkdir(dest)
    temp_dir = tempfile.mkdtemp(dir=dest)
    extract_command = ["unzip", installer, "-d", temp_dir, "data/noarch/*"]
    run_command(extract_command)

    # Move files from temp dir to game folder
    game_files_dir = os.path.join(temp_dir, "data/noarch")
    update_dir(game_files_dir, dest)

    rmdir(temp_dir)

    # Save list of file names to text file
    text_file = os.path.join(dest, "files.txt")
    list_files_command = [
        "unzip", "-Z", "-1", installer, "data/noarch/*", ">>", text_file
    ]
    run_command(list_files_command, shell=True)
