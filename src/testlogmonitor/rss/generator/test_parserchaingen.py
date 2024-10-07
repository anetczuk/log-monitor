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
from logmonitor.rss.generator.parserchaingen import ParserChainGenerator


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def sort_dict(data_dict):
    return dict(sorted(data_dict.items()))


class ParserChainGeneratorTest(unittest.TestCase):

    def test_parse_traceback(self):
        log_path = get_data_path("log_trace.txt")
        chain_params = {
            "chain": [
                {
                    "parser": "logging",
                    "label": "log-monitor-a",
                    "enabled": True,
                    "outfile": "log-monitor.xml",
                    "params": {
                        "logfile": log_path,
                        "fmt": "%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(name)s:%(funcName)s"
                        " [%(filename)s:%(lineno)d] %(message)s",
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                        "loglevel": "WARNING",
                    },
                },
                {
                    "parser": "pytraceback",
                    "label": "log-monitor-b",
                    "enabled": True,
                    "outfile": "log-monitor.xml",
                    "params": {"logfile": log_path},
                },
            ],
        }
        generator = ParserChainGenerator("testgen", "parser-chain.txt", **chain_params)
        gen_data = generator.generate()
        self.assertEqual({"parser-chain.txt"}, gen_data.keys())
        content = gen_data["parser-chain.txt"]
        self.assertEqual(3540, len(content))
