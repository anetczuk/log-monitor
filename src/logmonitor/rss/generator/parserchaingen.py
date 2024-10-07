#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import logging

from feedgen.feed import FeedGenerator

from logmonitor.parser.pytracebackparser import PyTracebackParser
from logmonitor.rss.generator.rssgenerator import RSSGenerator
from logmonitor.rss.utils import init_feed_gen


_LOGGER = logging.getLogger(__name__)


class ParserChainGenerator(RSSGenerator):
    def __init__(self, name=None, outfile=None, chain=None):
        # prevents cyclic import error
        from logmonitor.rss.generatorspawn import spawn_generator_from_cfg

        super().__init__(outfile)
        self.parser = PyTracebackParser()
        self.name = name

        self.generators = []
        for parser_conf in chain:
            generator_tuple = spawn_generator_from_cfg(parser_conf)
            self.generators.append(generator_tuple)

    def get_name(self) -> str:
        return self.name

    def generate_feed(self) -> FeedGenerator:
        feed_gen = init_feed_gen("http://not.set")  # have to be semantically valid
        feed_gen.title(self.outfile)
        feed_gen.description(self.outfile)

        for gen_state in self.generators:
            gen = gen_state[1]
            data = gen.generate_feed()
            entries = data.entry()
            for item in entries:
                feed_gen.add_entry(item)

        return feed_gen
