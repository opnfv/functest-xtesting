#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import unittest


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('Hello World'.upper(),
                         'HELLO WORLD')
