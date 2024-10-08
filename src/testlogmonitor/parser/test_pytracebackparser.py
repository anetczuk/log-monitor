#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import datetime
import unittest

from logmonitor.parser.pytracebackparser import PyTracebackParser

from testlogmonitor.data import get_data_path


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def sort_dict(data_dict):
    return dict(sorted(data_dict.items()))


class PyTracebackParserTest(unittest.TestCase):

    def test_parse_traceback(self):
        parser = PyTracebackParser()
        log_pagh = get_data_path("log_trace.txt")
        response = parser.parse_file(log_pagh)

        self.assertEqual(1, len(response))

        mod_time = response[0][0]
        # self.assertEqual(1728075360.8512435, mod_time)
        datestamp = datetime.datetime.fromtimestamp(mod_time)
        self.assertEqual(datetime.datetime(2024, 10, 4, 22, 56, 0, 851243), datestamp)

        message_id = response[0][1]
        self.assertEqual("3b6169c3311e84eab8aec3b80628c96a", message_id)

        message_lines = response[0][2]
        self.assertEqual("Traceback (most recent call last):", message_lines[0])
        self.assertEqual(
            """RuntimeError: file /tmplog/log.txt: unable to match pattern to line 1: """
            """2024-10-04 15:09:57,773 INFO     Thread-2 (_runLoop) package:add_offer [google.py:111] """
            """getting offer details: https://www.google.com""",
            message_lines[-1],
        )

    def test_parse_traceback_hint(self):
        parser = PyTracebackParser()
        log_pagh = get_data_path("log_trace_hint.txt")
        response = parser.parse_file(log_pagh)

        self.assertEqual(1, len(response))

        mod_time = response[0][0]
        # self.assertEqual(1728075360.8512435, mod_time)
        datestamp = datetime.datetime.fromtimestamp(mod_time)
        self.assertEqual(datetime.datetime(2024, 10, 8, 17, 1, 42, 186263), datestamp)

        message_id = response[0][1]
        self.assertEqual("ee87529631a74faf35dc6810a8e2b06f", message_id)

        message_lines = response[0][2]
        self.assertEqual("Traceback (most recent call last):", message_lines[0])
        self.assertEqual(
            """  start(self): too many arguments""",
            message_lines[-1],
        )
