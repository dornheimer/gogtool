"""Module for parsing config files."""

from gogtool.helper.log import logger

bool_dict = {'true': True, 'false': False}


def parse_config(path, key=None):
    """Return dictionary with options -> values from lgog config file."""
    with open(path, 'r') as config_file:
        lines = config_file.readlines()
        config_dict = dict(line.strip().split(" = ") for line in lines)
    if key:
        try:
            key_value = config_dict[key]
            logger.debug(f"Succesfully parsed config file with key: '{key}'")
            if is_int(key_value):
                return int(key_value)
            return bool_dict.get(key_value, key_value)
        except KeyError:
            logger.error(f"Invalid key: '{key}'", exc_info=True)

    logger.debug("Succesfully parsed config file")
    return config_dict


def is_int(string):
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True
