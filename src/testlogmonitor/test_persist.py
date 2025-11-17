#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#


import unittest

from logmonitor import persist


class FileMock:

    def read(self):
        return None

    def readline(self):
        return None


class RenamingUnpicklerTest(unittest.TestCase):
    def setUp(self):
        ## Called before testfunction is executed
        pass

    def tearDown(self):
        ## Called after testfunction was executed
        pass

    def test_dict_property(self):
        class TestClass:

            def __init__(self):
                self._field = None

            @property
            def field(self):
                return self._field

            @field.setter
            def field(self, value):
                self._field = value

        testObject = TestClass()
        self.assertTrue("_field" in testObject.__dict__)
        self.assertTrue("field" not in testObject.__dict__)

    def test_find_name_callable(self):
        def mapper_function(module, name):
            name_map = {"aaa": "bbb"}
            return (name_map.get(module, module), name)

        file = FileMock()
        unpicker = persist.RenamingUnpickler(file, module_mapper=mapper_function)

        module, name = unpicker.find_name("aaa", "xxx")

        self.assertEqual(module, "bbb")
        self.assertEqual(name, "xxx")

    def test_find_name_object(self):
        class MapperClass:
            def __call__(self, module, name):
                name_map = {"aaa": "bbb"}
                return (name_map.get(module, module), name)

        mapper = MapperClass()

        file = FileMock()
        unpicker = persist.RenamingUnpickler(file, module_mapper=mapper)

        module, name = unpicker.find_name("aaa", "xxx")

        self.assertEqual(module, "bbb")
        self.assertEqual(name, "xxx")
