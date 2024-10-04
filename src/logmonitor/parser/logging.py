#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

from pygrok.pygrok import Grok

from logmonitor.parser.abcparser import ABCParser


class LoggingParser(ABCParser):

    # thread name have optional function name, e.g. 'Thread-2 (_runner)'
    CUSTOM_PATS = {"THREADNAME": "%{NOTSPACE}(?:%{SPACE}%{NOTSPACE})"}

    # list prepared based on https://docs.python.org/3/library/logging.html#logrecord-attributes
    TOKENS = {
        "asctime": ("s", "DATA"),
        "created": ("f", "NUMBER"),
        "filename": ("s", "NOTSPACE"),
        "funcName": ("s", "NOTSPACE"),
        "levelname": ("s", "NOTSPACE"),
        "levelno": ("s", "NOTSPACE"),
        "lineno": ("d", "NONNEGINT"),
        "message": ("s", "GREEDYDATA"),
        "module": ("s", "NOTSPACE"),
        "msecs": ("d", "NONNEGINT"),
        "name": ("s", "NOTSPACE"),
        "pathname": ("s", "NOTSPACE"),
        "process": ("d", "NONNEGINT"),
        "processName": ("s", "NOTSPACE"),
        "relativeCreated": ("d", "NONNEGINT"),
        "thread": ("d", "NONNEGINT"),
        "threadName": ("s", "THREADNAME"),
        "taskName": ("s", "NOTSPACE"),
    }

    # list prepared based on https://docs.python.org/3/library/time.html#time.strftime
    DATETIME_TOKENS = {
        "a": "WORD",
        "A": "WORD",
        "b": "WORD",
        "B": "WORD",
        # c
        "d": "NONNEGINT",
        "f": "NONNEGINT",
        "H": "NONNEGINT",
        "I": "NONNEGINT",
        "j": "NONNEGINT",
        "m": "NONNEGINT",
        "M": "NONNEGINT",
        "p": "WORD",
        "S": "NONNEGINT",
        "U": "NONNEGINT",
        "w": "NONNEGINT",
        "W": "NONNEGINT",
        # x
        # X
        "y": "NONNEGINT",
        "Y": "NONNEGINT",
        # z
        # Z
    }

    def __init__(self, fmt=None, datefmt=None, pattern=None):
        super().__init__()

        if pattern is None:
            pattern = self.parse_format(fmt)
        self.grok = Grok(pattern, custom_patterns=self.CUSTOM_PATS)

        self.datetime_grok = None
        if datefmt:
            datetime_pattern = self.parse_datetime(datefmt)
            self.datetime_grok = Grok(datetime_pattern)

    def parse_content(self, content, file_path=None):
        ret_list = []
        lines = content.splitlines()
        for line_index, raw_line in enumerate(lines):
            found = self.grok.match(raw_line)
            if found is None:
                # continuation of multiline log
                if ret_list:
                    prev_entry = ret_list[-1]
                    self._append_text(prev_entry, raw_line)
                else:
                    raise RuntimeError(
                        f"file {file_path}: unable to match pattern '{self.grok.pattern}'"
                        f" to line {line_index + 1}: {raw_line}"
                    )
                continue

            if self.datetime_grok:
                datetime_string = found.get("asctime")
                if datetime_string:
                    datetime_found = self.datetime_grok.match(datetime_string)
                    if datetime_found:
                        found["asctime"] = datetime_found

            ret_list.append([raw_line, found])
        return ret_list

    @staticmethod
    def _append_text(data_entry, text):
        data_dict = data_entry[1]
        if "message" not in data_dict:
            # there should be message, because there is next line of multiline log
            raise RuntimeError("unexpected log")

        data_entry[0] += "\n" + text
        data_dict["message"] += "\n" + text

    @staticmethod
    # style='%' -- not supported yet
    def parse_format(fmt=None):
        if fmt is None:
            return ""
        pattern_list = []
        end_pos = 0
        while end_pos >= 0:
            # find start of next token
            start_pos = fmt.find("%(", end_pos)
            if start_pos < 0:
                # no more tokens
                postfix = fmt[end_pos:]
                if postfix:
                    postfix = escape_regex(postfix)
                    pattern_list.append(postfix)
                break

            # get token prefix
            prefix = fmt[end_pos:start_pos]
            if prefix:
                prefix = escape_regex(prefix)
                pattern_list.append(prefix)
            start_pos += 2

            # get token name
            end_pos = fmt.find(")", start_pos)
            if end_pos < 0:
                raise ValueError("invalid pattern - no token end")
            token = fmt[start_pos:end_pos]
            end_pos += 1

            # get token data
            token_data = LoggingParser.TOKENS.get(token)
            if token_data is None:
                raise ValueError(f"unknown token: {token}")
            token_type = token_data[0]

            # get token type modifier
            type_pos = fmt.find(token_type, end_pos)
            if type_pos < 0:
                raise ValueError("invalid pattern - no token type")
            token_modifier = fmt[end_pos:type_pos]
            end_pos = type_pos + 1

            token_pattern = token_data[1]
            pattern = f"%{{{token_pattern}:{token}}}"
            pattern_list.append(pattern)

            if token_type in ("s", "d"):  # nosec
                if token_modifier:
                    # case of string with reserved length
                    # if string is shorter than reservation, then empty spaces will be filled with spaces
                    pattern_list.append("%{SPACE}")

        pattern = "".join(pattern_list)
        return pattern

    @staticmethod
    def parse_datetime(datefmt=None):
        if datefmt is None:
            return ""
        pattern_list = []
        end_pos = 0
        while end_pos >= 0:
            # find start of next token
            start_pos = datefmt.find("%", end_pos)
            if start_pos < 0:
                # no more tokens
                postfix = datefmt[end_pos:]
                if postfix:
                    pattern_list.append(postfix)
                break

            # get token prefix
            prefix = datefmt[end_pos:start_pos]
            if prefix:
                pattern_list.append(prefix)
            start_pos += 1

            # get token name
            token = datefmt[start_pos]
            end_pos = start_pos + 1

            # get token data
            token_pattern = LoggingParser.DATETIME_TOKENS.get(token)
            if token_pattern is None:
                raise ValueError(f"unknown token: {token}")
            pattern = f"%{{{token_pattern}:{token}}}"
            pattern_list.append(pattern)

        pattern = "".join(pattern_list)
        return pattern
        # return "%{GREEDYDATA:xxx}"#-%{NONNEGINT:m}-%{NONNEGINT:d} %{NONNEGINT:H}:%{NONNEGINT:M}:%{NONNEGINT:S}"


def escape_regex(pattern):
    pattern = pattern.replace("[", "\\[")
    pattern = pattern.replace("]", "\\]")
    return pattern
