#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
from typing import List, Any

from logmonitor.parser.abcparser import ABCParser
from logmonitor.utils import calculate_hash


class PyTracebackParser(ABCParser):

    FIRST_LINE = "Traceback (most recent call last):"
    RETHROW_LINES = set(
        [
            "The above exception was the direct cause of the following exception:",
            "During handling of the above exception, another exception occurred:",
        ]
    )

    def __init__(self, linesbefore=0):
        super().__init__()
        self.lines_before = linesbefore

    def parse_content(self, content, file_path=None) -> List[Any]:
        ret_list = []
        lines = content.splitlines()
        traceback_content = None
        reason_line = False
        for line_index, raw_line in enumerate(lines):
            if raw_line == self.FIRST_LINE:
                # traceback first line
                if traceback_content is None:
                    traceback_content = []
                if self.lines_before > 0:
                    start_index = max(0, line_index - self.lines_before)
                    traceback_content = lines[start_index:line_index]
                reason_line = False  # needed in case of rethorw to allow next rethrow
                traceback_content.append(raw_line)
                continue

            if traceback_content is None:
                # no traceback state
                continue

            if raw_line == "":
                # in traceback empty lines can happen e.g. splitting any rethreow parts
                traceback_content.append(raw_line)
            elif raw_line.startswith("  "):
                # indent in traceback
                traceback_content.append(raw_line)
            elif raw_line in self.RETHROW_LINES:
                # indicator of next traceback (rethrow)
                reason_line = False
                traceback_content.append(raw_line)
            else:
                if reason_line is False:
                    # traceback message with reason - there may be hint data
                    traceback_content.append(raw_line)
                    reason_line = True
                else:
                    # no more traceback data
                    found_entry = self._calculate_entry(lines, line_index, traceback_content, file_path)
                    ret_list.append(found_entry)
                    reason_line = False
                    traceback_content = None

        if traceback_content:
            last_line_index = len(lines)
            found_entry = self._calculate_entry(lines, last_line_index, traceback_content, file_path)
            ret_list.append(found_entry)

        return ret_list

    def _calculate_entry(self, log_lines, line_index, traceback_content, file_path):
        mod_time = os.path.getmtime(file_path)
        prev_lines = log_lines[: line_index + 1]
        prev_content = "\n".join(prev_lines)
        lines_md5 = calculate_hash(prev_content)
        return [mod_time, lines_md5, traceback_content]
