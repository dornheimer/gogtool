from lgog.helper.log import logger


def parse_config(path, key=None):
    """Return dictionary with options -> values from lgog config file."""
    with open(path, 'r') as config_file:
        lines = config_file.readlines()
        config_dict = dict(line.strip().split(" = ") for line in lines)
    if key:
        try:
            key_value = config_dict[key]
            logger.debug(f"Succesfully parsed config file with key: '{key}'")
            return key_value
        except KeyError:
            logger.error(f"Invalid key: '{key}'", exc_info=True)

    logger.debug("Succesfully parsed config file")
    return config_dict
