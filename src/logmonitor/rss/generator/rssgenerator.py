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
from feedgen.feed import FeedGenerator
from logmonitor.rss.utils import dumps_feed_gen


_LOGGER = logging.getLogger(__name__)


#
class RSSGenerator(ABC):

    def __init__(self, outfile):
        self.outfile = outfile

    @abstractmethod
    def get_name(self) -> str:
        """Return generator identifier."""
        raise NotImplementedError("method not implemented")

    def generate(self) -> Dict[str, str]:
        """Grab data and generate RSS feed.

        Returned dict keys are relative paths to files where content from value will be stored to.
        Returns None if there was problem with generator.
        """
        feed = self.generate_feed()
        if feed is None:
            return None
        content = dumps_feed_gen(feed)
        return {self.outfile: content}

    @abstractmethod
    def generate_feed(self) -> FeedGenerator:
        """Grab data and generate RSS feed object."""
        raise NotImplementedError("method not implemented")

    # override if needed
    def close(self):
        """Request close on any open resources."""
