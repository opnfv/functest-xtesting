#!/usr/bin/env python

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import logging
import unittest

import mock

from xtesting.ci import tier_handler


class TierHandlerTesting(unittest.TestCase):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        self.test = mock.Mock()
        attrs = {'get_name.return_value': 'test_name'}
        self.test.configure_mock(**attrs)
        self.tier = tier_handler.Tier(
            'test_tier', 'test_order', 'test_desc')
        self.testcase = tier_handler.TestCase(
            'test_name', 'true', False, 'test_criteria',
            True, description='test_desc', project='project_name')
        self.testcase.str = self.testcase.__str__()
        self.tier.str = self.tier.__str__()

    def test_split_text(self):
        test_str = 'this is for testing'
        self.assertEqual(tier_handler.split_text(test_str, 10),
                         ['this is ', 'for ', 'testing '])

    def test_add_test(self):
        self.tier.add_test(self.test)
        self.assertEqual(self.tier.tests_array, [self.test])

    def test_get_skipped_test1(self):
        self.assertEqual(self.tier.get_skipped_test(), [])

    def test_get_skipped_test2(self):
        self.tier.skip_test(self.test)
        self.assertEqual(self.tier.get_skipped_test(), [self.test])

    def test_get_tests(self):
        self.tier.tests_array = [self.test]
        self.assertEqual(self.tier.get_tests(), [self.test])

    def test_get_test_names(self):
        self.tier.tests_array = [self.test]
        self.assertEqual(self.tier.get_test_names(), ['test_name'])

    def test_get_test(self):
        self.tier.tests_array = [self.test]
        with mock.patch.object(self.tier, 'is_test', return_value=True):
            self.assertEqual(self.tier.get_test('test_name'), self.test)

    def test_get_test_missing_test(self):
        self.tier.tests_array = [self.test]
        with mock.patch.object(self.tier, 'is_test', return_value=False):
            self.assertEqual(self.tier.get_test('test_name'), None)

    def test_get_name(self):
        self.assertEqual(self.tier.get_name(), 'test_tier')

    def test_get_order(self):
        self.assertEqual(self.tier.get_order(), 'test_order')

    def test_testcase_get_name(self):
        self.assertEqual(self.tier.get_name(), 'test_tier')

    def test_testcase_is_enabled(self):
        self.assertEqual(self.testcase.is_enabled(), 'true')

    def test_testcase_get_criteria(self):
        self.assertEqual(self.testcase.get_criteria(), 'test_criteria')

    def test_testcase_is_blocking(self):
        self.assertTrue(self.testcase.is_blocking())

    def test_testcase_get_project(self):
        self.assertEqual(self.testcase.get_project(), 'project_name')

    def test_testcase_get_order(self):
        self.assertEqual(self.tier.get_order(), 'test_order')


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
