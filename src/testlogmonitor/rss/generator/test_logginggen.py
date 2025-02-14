#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import unittest

from testlogmonitor.data import get_data_path
from logmonitor.rss.generator.logginggen import LoggingGenerator


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def sort_dict(data_dict):
    return dict(sorted(data_dict.items()))


class LoggingGeneratorTest(unittest.TestCase):

    def test_generate(self):
        log_path = get_data_path("log_special_chars.txt")
        parser_params = {
            "fmt": "%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(name)s:%(funcName)s"
            " [%(filename)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "loglevel": "WARNING",
        }
        generator = LoggingGenerator("testgen", "outtraces.xml", log_path, **parser_params)
        gen_data = generator.generate()
        self.assertEqual({"outtraces.xml"}, gen_data.keys())
        content = gen_data["outtraces.xml"]
        self.assertEqual(1022, len(content))
