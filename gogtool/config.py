import copy
import logging
import os

import yaml

DEFAULT_USER_CONFIG_PATH = os.path.expanduser('~/.gogtool.yaml')

DEFAULT_CONFIG = {
    'install_dir': '~/GOG Games',
    'lgog_config_path': '~/.config/lgogdownloader/config.cfg',
    'lgog_data_path': '~/.cache/lgogdownloader/gamedetails.json',
}

logger = logging.getLogger(__name__)


def convert_bool(bool_string):
    if bool_string == 'true':
        return True
    elif bool_string == 'false':
        return False
    else:
        return bool_string


def load_user_config(config_file=None):
    env_config = os.getenv('GOGTOOL_CONFIG', None)
    if env_config is not None:
        logger.debug("GOGTOOL_CONFIG is set")
        config_file = os.path.expanduser(env_config)
    if config_file is None or not os.path.exists(config_file):
        return {}
    with open(config_file) as f:
        logger.debug("Loading user config: %s", config_file)
        return yaml.load(f) or {}


def load_lgog_config(config_file):
    logger.debug("Loading lgogdownloader config: %s", config_file)
    with open(config_file) as f:
        lines = f.readlines()

    config = dict(line.strip().split(" = ") for line in lines)
    return {k: convert_bool(v) for k, v in config.items()}


def update_config(original, new):
    config = copy.deepcopy(original)
    config.update(new)
    return config


def configure_gogtool(config_file=None):
    if config_file is None:
        config_file = DEFAULT_USER_CONFIG_PATH
    user_config = load_user_config(config_file)
    if user_config:
        config = update_config(DEFAULT_CONFIG, user_config)
    else:
        logger.debug("Loading default config")
        config = DEFAULT_CONFIG

    # Expand home alias if used
    config['install_dir'] = os.path.expanduser(config['install_dir'])
    config['lgog_config_path'] = os.path.expanduser(config['lgog_config_path'])
    config['lgog_data_path'] = os.path.expanduser(config['lgog_data_path'])

    lgog_config = load_lgog_config(config['lgog_config_path'])
    # User settings have priority
    config['download_dir'] = config.get('download_dir') or \
        lgog_config['directory']
    config['lgogdownloader'] = update_config(
        lgog_config,
        config.get('lgogdownloader', {})
    )

    return config
