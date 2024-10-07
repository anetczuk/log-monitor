#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging
from typing import Dict, Any

import pkgutil

from logmonitor.configfileyaml import ConfigField
from logmonitor.rss.generator.rssgenerator import RSSGenerator

import logmonitor.rss.generator


_LOGGER = logging.getLogger(__name__)


# ============================================


_GENERATOR_DICT = {
    "logging": "LoggingGenerator",
    "pytraceback": "PyTracebackGenerator",
    "parserchain": "ParserChainGenerator",
}


def get_gen_def(generator_class):
    generators_module = logmonitor.rss.generator
    generators_path = os.path.dirname(generators_module.__file__)
    modules_list = pkgutil.iter_modules([generators_path])

    for mod_info in modules_list:
        mod_name = mod_info.name
        mod_full_name = f"{generators_module.__name__}.{mod_name}"
        mod = __import__(mod_full_name, fromlist=[""])

        try:
            gen_class_def = getattr(mod, generator_class)
            return gen_class_def
        except AttributeError:
            continue

    return None


def spawn_generator(
    generator_type, generator_label, generator_outfile, generator_params_dict: Dict[Any, Any] = None
) -> RSSGenerator:
    generator_class = _GENERATOR_DICT.get(generator_type)
    if generator_class is None:
        _LOGGER.warning("unable to load generator %s", generator_type)
        return None
    try:
        gen_def = get_gen_def(generator_class)
        return gen_def(generator_label, generator_outfile, **generator_params_dict)
    except BaseException:
        _LOGGER.exception("unable to load generator %s", generator_type)
        return None


def spawn_generator_from_cfg(gen_params_dict):
    gen_type = gen_params_dict.get(ConfigField.PARSER_TYPE.value)
    if not gen_type:
        _LOGGER.warning("unable to get generator id from params: %s", gen_params_dict)
        return None
    if not gen_params_dict.get(ConfigField.ENABLED.value, True):
        _LOGGER.warning("generator %s disabled", gen_type)
        return None

    try:
        gen_label = gen_params_dict.get(ConfigField.LABEL.value, None)
        gen_outfile = gen_params_dict.get(ConfigField.OUTFILE.value, None)
        gen_inner_params = gen_params_dict.get(ConfigField.GEN_PARAMS.value, None)
        generator: RSSGenerator = spawn_generator(gen_type, gen_label, gen_outfile, gen_inner_params)
        if not generator:
            _LOGGER.warning("unable to get generator %s", gen_type)
            return None
        gen_state = (gen_type, generator)
        return gen_state

    except Exception as exc:  # pylint: disable=W0703
        # unable to authenticate - will not be possible to generate content
        _LOGGER.exception("error during initialization of %s: %s", gen_type, exc)

    return None
