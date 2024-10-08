#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import unittest

from logmonitor.utils import normalize_string


class UtilsTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_normalize_string_control_char(self):
        string = ["aaa\x02bbb\nccc"]
        converted = []
        converted.append(normalize_string(string[0]))
        self.assertEqual(["aaa bbb\nccc"], converted)
