#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import logging

from feedgen.feed import FeedGenerator

from logmonitor.rss.generator.rssgenerator import RSSGenerator
from logmonitor.parser.loggingparser import LoggingParser
from logmonitor.rss.utils import init_feed_gen
from logmonitor.utils import calculate_hash, string_iso_to_date


_LOGGER = logging.getLogger(__name__)


class LoggingGenerator(RSSGenerator):
    def __init__(self, name=None, outfile=None, logfile=None, loglevel=None, **kwargs):
        super().__init__(outfile)
        self.parser = LoggingParser(**kwargs)
        self.name = name
        self.logfile = logfile
        self.loglevelthreshhold = loglevel

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
        raw_log_entry = data_entry[0]
        data_dict = data_entry[1]

        levelname = data_dict["levelname"]
        if not self._check_loglevel(levelname):
            return

        filename = data_dict["filename"]
        log_datetime_data = data_dict["asctime"]
        log_datetime = get_log_date(log_datetime_data)

        feed_item = feed_gen.add_entry()

        # calculating hash from data dict is "fragile"
        # log_hash = calculate_dict_hash(data_dict)
        log_hash = calculate_hash(raw_log_entry)
        feed_item.id(log_hash)

        feed_item.title(f"{self.name}: {levelname} - {filename}")
        feed_item.author({"name": self.name, "email": self.name})

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

    def _check_loglevel(self, entry_level) -> bool:
        curr_priority = get_log_priority(entry_level)
        threshold_priority = get_log_priority(self.loglevelthreshhold)
        return curr_priority >= threshold_priority


def get_log_date(date_dict):
    datetime_string = (
        f"{date_dict['Y']}-{date_dict['m']}-{date_dict['d']} {date_dict['H']}:{date_dict['M']}:{date_dict['S']}"
    )
    return string_iso_to_date(datetime_string)


LEVEL_MAPPING = {None: 0, "DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


def get_log_priority(level_name):
    return LEVEL_MAPPING[level_name]
