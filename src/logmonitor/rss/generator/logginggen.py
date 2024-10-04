#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import logging
from typing import Dict

from logmonitor.rss.generator.rssgenerator import RSSGenerator
from logmonitor.parser.logging import LoggingParser
from logmonitor.rss.utils import init_feed_gen, dumps_feed_gen
from logmonitor.utils import calculate_hash, string_iso_to_date


_LOGGER = logging.getLogger(__name__)


class LoggingGenerator(RSSGenerator):
    def __init__(self, name=None, logfile=None, loglevel=None, **kwargs):
        super().__init__()
        self.parser = LoggingParser(**kwargs)
        self.logname = name
        self.logfile = logfile
        self.loglevelthreshhold = loglevel

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
        raw_log = data_entry[0]
        data_dict = data_entry[1]

        levelname = data_dict["levelname"]
        if not self._check_loglevel(levelname):
            return

        filename = data_dict["filename"]
        log_datetime_data = data_dict["asctime"]
        log_datetime = get_log_date(log_datetime_data)

        feed_item = feed_gen.add_entry()

        # calculating hash from data dict is "fragile"
        # data_hash = calculate_dict_hash(data_dict)
        data_hash = calculate_hash(raw_log)
        feed_item.id(data_hash)

        feed_item.title(f"{self.logname}: {levelname} - {filename}")
        feed_item.author({"name": self.logname, "email": self.logname})

        # fill description
        content = f"""
<div>
<pre>
{raw_log}
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
