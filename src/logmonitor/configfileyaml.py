#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging
from enum import Enum, unique
import yaml

from logmonitor.utils import get_app_datadir


_LOGGER = logging.getLogger(__name__)


# ==================================================


@unique
class ConfigField(Enum):
    GENERAL = "general"
    GENITEM = "item"

    STARTUPDELAY = "startupdelay"
    STARTSERVER = "startserver"
    PORT = "port"
    REFRESHTIME = "refreshtime"
    DATAROOT = "dataroot"
    LOGDIR = "logdir"
    LOGVIEWER = "logviewer"

    PARSER_ID = "parser"
    ENABLED = "enabled"
    GEN_PARAMS = "params"


# ==================================================


def load_config(config_path):
    config_dict = load_raw(config_path)
    if not config_dict:
        return config_dict

    # set default value of data directory if not set
    general_section = config_dict.get(ConfigField.GENERAL.value, {})
    data_root = general_section.get(ConfigField.DATAROOT.value)
    data_root = specify_dir(data_root, config_path, "data")
    general_section[ConfigField.DATAROOT.value] = data_root

    log_dir = general_section.get(ConfigField.LOGDIR.value)
    log_dir = specify_dir(log_dir, config_path, "log")
    general_section[ConfigField.LOGDIR.value] = log_dir

    return config_dict


def specify_dir(dir_value, config_path, default_dir):
    if dir_value is None:
        data_dir = get_app_datadir()
        dir_value = os.path.join(data_dir, default_dir)
    elif not os.path.isabs(dir_value):
        # relative path - make it relative to config file
        config_dir = os.path.dirname(config_path)
        dir_value = os.path.join(config_dir, dir_value)
    dir_value = os.path.abspath(dir_value)
    return dir_value


def load_raw(config_path):
    if not config_path:
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.unsafe_load(f)
    except FileNotFoundError:
        _LOGGER.warning("could not load config file '%s' - using default configuration", config_path)
    return {}
