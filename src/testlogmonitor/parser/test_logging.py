#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest

from logmonitor.parser.logging import LoggingParser


def sort_dict(data_dict):
    return dict(sorted(data_dict.items()))


class LoggingParserTest(unittest.TestCase):
    def test_parse_format(self):
        fmt = (
            "%(asctime)s,%(msecs)-3d %(levelname)-8s"
            " %(threadName)s %(name)s:%(funcName)s [%(filename)s:%(lineno)d] %(message)s"
        )
        pattern = LoggingParser.parse_format(fmt)
        self.assertEqual(
            pattern,
            "%{DATA:asctime},%{NONNEGINT:msecs}%{SPACE} %{NOTSPACE:levelname}%{SPACE} %{NOTSPACE:threadName}"
            " %{NOTSPACE:name}:%{NOTSPACE:funcName} \\[%{NOTSPACE:filename}:%{NONNEGINT:lineno}\\]"
            " %{GREEDYDATA:message}",
        )

    def test_parse_datetime_format(self):
        datefmt = "%Y-%m-%d %H:%M:%S"
        pattern = LoggingParser.parse_datetime(datefmt)
        self.assertEqual(
            pattern, "%{NONNEGINT:Y}-%{NONNEGINT:m}-%{NONNEGINT:d} %{NONNEGINT:H}:%{NONNEGINT:M}:%{NONNEGINT:S}"
        )

    def test_parse_01(self):
        self.maxDiff = None
        parser = LoggingParser(
            "%(asctime)s,%(msecs)-3d %(levelname)-8s"
            " %(threadName)s %(name)s:%(funcName)s [%(filename)s:%(lineno)d] %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        log_content = (
            "2024-09-08 22:41:08,605 INFO     MainThread rsscast.source.youtube.convert_ddownr_com:convert_yt"
            " [convert_ddownr_com.py:86] downloading completed"
        )
        response = parser.parse_content(log_content)
        data = {
            "asctime": {"H": "22", "M": "41", "S": "08", "Y": "2024", "d": "08", "m": "09"},
            "msecs": "605",
            "levelname": "INFO",
            "threadName": "MainThread",
            "name": "rsscast.source.youtube.convert_ddownr_com",
            "funcName": "convert_yt",
            "filename": "convert_ddownr_com.py",
            "lineno": "86",
            "message": "downloading completed",
        }
        self.assertListEqual([[log_content, sort_dict(data)]], response)

    def test_parse_02(self):
        # log entry with two digits milliseconds

        self.maxDiff = None
        parser = LoggingParser(
            "%(asctime)s,%(msecs)-3d %(levelname)-8s"
            " %(threadName)s %(name)s:%(funcName)s [%(filename)s:%(lineno)d] %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        log_content = (
            "2024-09-09 20:30:24,86  DEBUG    MainThread __main__:main [main.py:89] Starting the application"
        )
        response = parser.parse_content(log_content)
        data = {
            "asctime": {"H": "20", "M": "30", "S": "24", "Y": "2024", "d": "09", "m": "09"},
            "msecs": "86",
            "levelname": "DEBUG",
            "threadName": "MainThread",
            "name": "__main__",
            "funcName": "main",
            "filename": "main.py",
            "lineno": "89",
            "message": "Starting the application",
        }
        self.assertListEqual([[log_content, sort_dict(data)]], response)

    def test_parse_multiline(self):
        self.maxDiff = None
        parser = LoggingParser(
            "%(asctime)s,%(msecs)-3d %(levelname)-8s"
            " %(threadName)s %(name)s:%(funcName)s [%(filename)s:%(lineno)d] %(message)s"
        )
        log_content = (
            "2024-09-08 22:41:08,605 INFO     MainThread rsscast.source.youtube.convert_ddownr_com:convert_yt"
            " [convert_ddownr_com.py:86] downloading completed\nsecond log line\nthird log line"
        )
        response = parser.parse_content(log_content)
        data = {
            "asctime": "2024-09-08 22:41:08",
            "msecs": "605",
            "levelname": "INFO",
            "threadName": "MainThread",
            "name": "rsscast.source.youtube.convert_ddownr_com",
            "funcName": "convert_yt",
            "filename": "convert_ddownr_com.py",
            "lineno": "86",
            "message": "downloading completed\nsecond log line\nthird log line",
        }
        self.assertListEqual([[log_content, sort_dict(data)]], response)
