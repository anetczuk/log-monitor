#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

from typing import List, Any
from abc import ABC, abstractmethod

from logmonitor.utils import read_data


class ABCParser(ABC):
    """Abstract parser."""

    def __init__(self):
        pass

    def parse_file(self, file_path) -> List[Any]:
        try:
            content = read_data(file_path)
            return self.parse_content(content, file_path=file_path)
        except FileNotFoundError:
            return None

    @abstractmethod
    def parse_content(self, content, file_path=None) -> List[Any]:
        raise NotImplementedError("method not implemented")
