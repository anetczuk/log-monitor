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
    def __init__(self, name=None, logfile=None, **kwargs):
        super().__init__()
        self.parser = LoggingParser(**kwargs)
        self.logname = name
        self.logfile = logfile

    def generate(self) -> Dict[str, str]:
        log_list = self.parser.parse_file(self.logfile)

        feed_gen = init_feed_gen("not-set")
        feed_gen.title(self.logname)
        feed_gen.description(self.logname)

        _LOGGER.info("found %s items", len(log_list))
        for entry in log_list:
            add_log_entry(feed_gen, self.logname, entry)

        content = dumps_feed_gen(feed_gen)
        return {self.logname: content}


def add_log_entry(feed_gen, label, data_entry):
    raw_log = data_entry[0]
    data_dict = data_entry[1]

    filename = data_dict["filename"]
    levelname = data_dict["levelname"]
    log_datetime_data = data_dict["asctime"]
    log_datetime = get_log_date(log_datetime_data)

    feed_item = feed_gen.add_entry()

    # calculating hash from data dict is "fragile"
    # data_hash = calculate_dict_hash(data_dict)
    data_hash = calculate_hash(raw_log)
    feed_item.id(data_hash)

    feed_item.title(f"{label}: {levelname} - {filename}")
    feed_item.author({"name": label, "email": label})

    # fill description
    feed_item.content(raw_log)

    # fill publish date
    feed_item.pubDate(log_datetime)
    # feed_item.link(href=desc_url, rel="alternate")
    # feed_item.link( href=desc_url, rel='via')        # does not work in thunderbird


def get_log_date(date_dict):
    datetime_string = f"{date_dict['Y']}-{date_dict['m']}-{date_dict['d']} {date_dict['H']}:{date_dict['M']}:{date_dict['S']}"
    return string_iso_to_date(datetime_string)
