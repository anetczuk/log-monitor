#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import logging
from typing import Dict
import datetime

from logmonitor.rss.generator.rssgenerator import RSSGenerator
from logmonitor.rss.utils import init_feed_gen, dumps_feed_gen
from logmonitor.utils import add_timezone
from logmonitor.parser.pytracebackparser import PyTracebackParser


_LOGGER = logging.getLogger(__name__)


class PyTracebackGenerator(RSSGenerator):
    def __init__(self, name=None, logfile=None, **_kwargs):
        super().__init__()
        self.parser = PyTracebackParser()
        self.logname = name
        self.logfile = logfile

    def get_id(self) -> str:
        return self.logname

    def generate(self) -> Dict[str, str]:
        log_list = self.parser.parse_file(self.logfile)
        if log_list is None:
            _LOGGER.info("generator %s file %s does not exist", self.logname, self.logfile)
            return {self.logname: None}

        feed_gen = init_feed_gen("http://not.set")  # have to be semantically valid
        feed_gen.title(self.logname)
        feed_gen.description(self.logname)

        _LOGGER.info("found %s items", len(log_list))
        for entry in log_list:
            self._add_log_entry(feed_gen, entry)

        content = dumps_feed_gen(feed_gen)
        return {self.logname: content}

    def _add_log_entry(self, feed_gen, data_entry):
        mod_time = data_entry[0]
        log_hash = data_entry[1]
        msg_list = data_entry[2]
        exception = msg_list[-1]

        datestamp = datetime.datetime.fromtimestamp(mod_time)
        log_datetime = add_timezone(datestamp)

        feed_item = feed_gen.add_entry()
        feed_item.id(log_hash)
        feed_item.title(f"{self.logname}: {exception}")
        feed_item.author({"name": self.logname, "email": self.logname})

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
