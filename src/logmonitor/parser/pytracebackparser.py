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
                traceback_content = []
                if self.lines_before > 0:
                    start_index = max(0, line_index - self.lines_before)
                    traceback_content = lines[start_index:line_index]
                traceback_content.append(raw_line)
                continue

            if traceback_content is None:
                # no traceback state
                continue

            if raw_line.startswith("  "):
                traceback_content.append(raw_line)
            else:
                if reason_line is False:
                    # traceback message with reason - there may be hint data
                    traceback_content.append(raw_line)
                    reason_line = True
                else:
                    # no more traceback data
                    mod_time = os.path.getmtime(file_path)
                    prev_lines = lines[: line_index + 1]
                    prev_content = "\n".join(prev_lines)
                    lines_md5 = calculate_hash(prev_content)
                    ret_list.append([mod_time, lines_md5, traceback_content])
                    reason_line = False
                    traceback_content = None

        return ret_list
