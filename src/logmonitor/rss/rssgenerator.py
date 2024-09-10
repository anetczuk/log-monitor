#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import logging
from typing import Dict

from abc import ABC, abstractmethod


_LOGGER = logging.getLogger(__name__)


#
class RSSGenerator(ABC):
    @abstractmethod
    def generate(self) -> Dict[str, str]:
        """Grab data and generate RSS feed.

        Returned dict keys are relative paths to files where content from value will be stored to.
        Returns None if there was problem with generator.
        """
        raise NotImplementedError("method not implemented")

    # override if needed
    def close(self):
        """Request close on any open resources."""
