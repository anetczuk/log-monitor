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
from logmonitor.rss.generator.pytracebackgen import PyTracebackGenerator


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def sort_dict(data_dict):
    return dict(sorted(data_dict.items()))


class PyTracebackGeneratorTest(unittest.TestCase):

    def test_parse_traceback(self):
        log_path = get_data_path("log_trace.txt")
        generator = PyTracebackGenerator("testgen", log_path)
        gen_data = generator.generate()
        self.assertEqual({"testgen"}, gen_data.keys())
        content = gen_data["testgen"]
        self.assertEqual(2002, len(content))
