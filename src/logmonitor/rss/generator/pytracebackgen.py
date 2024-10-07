#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import logging
import datetime

from feedgen.feed import FeedGenerator

from logmonitor.rss.generator.rssgenerator import RSSGenerator
from logmonitor.rss.utils import init_feed_gen
from logmonitor.utils import add_timezone
from logmonitor.parser.pytracebackparser import PyTracebackParser


_LOGGER = logging.getLogger(__name__)


class PyTracebackGenerator(RSSGenerator):
    def __init__(self, name=None, outfile=None, logfile=None, **_kwargs):
        super().__init__(outfile)
        self.parser = PyTracebackParser()
        self.name = name
        self.logfile = logfile

    def get_name(self) -> str:
        return self.name

    def generate_feed(self) -> FeedGenerator:
        log_list = self.parser.parse_file(self.logfile)
        if log_list is None:
            _LOGGER.info("generator %s file %s does not exist", self.outfile, self.logfile)
            return {self.outfile: None}

        feed_gen = init_feed_gen("http://not.set")  # have to be semantically valid
        feed_gen.title(self.outfile)
        feed_gen.description(self.outfile)

        _LOGGER.info("found %s entries", len(log_list))
        for entry in log_list:
            self._add_log_entry(feed_gen, entry)

        return feed_gen

    def _add_log_entry(self, feed_gen, data_entry):
        mod_time = data_entry[0]
        log_hash = data_entry[1]
        msg_list = data_entry[2]
        exception = msg_list[-1]

        datestamp = datetime.datetime.fromtimestamp(mod_time)
        log_datetime = add_timezone(datestamp)

        feed_item = feed_gen.add_entry()
        feed_item.id(log_hash)
        feed_item.title(f"{self.name}: {exception}")
        feed_item.author({"name": self.name, "email": self.name})

        raw_log_entry = "\n".join(msg_list)

        # fill description
        content = f"""
<div>
<pre>
{raw_log_entry}
</pre>
</div>
"""
        feed_item.content(content)

        # fill publish date
        feed_item.pubDate(log_datetime)
        # feed_item.link(href=desc_url, rel="alternate")
        # feed_item.link( href=desc_url, rel='via')        # does not work in thunderbird
