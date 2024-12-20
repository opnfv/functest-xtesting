#!/usr/bin/env python

# Copyright (c) 2016 Ericsson AB and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring,too-many-instance-attributes

"""Tier and TestCase classes to wrap the testcases config file"""

import textwrap

import prettytable


class Tier():

    def __init__(self, name, description=""):
        self.tests_array = []
        self.skipped_tests_array = []
        self.name = name
        self.description = description

    def add_test(self, testcase):
        self.tests_array.append(testcase)

    def skip_test(self, testcase):
        self.skipped_tests_array.append(testcase)

    def get_tests(self):
        array_tests = []
        for test in self.tests_array:
            array_tests.append(test)
        return array_tests

    def get_skipped_test(self):
        return self.skipped_tests_array

    def get_test_names(self):
        array_tests = []
        for test in self.tests_array:
            array_tests.append(test.get_name())
        return array_tests

    def get_test(self, test_name):
        if self.is_test(test_name):
            for test in self.tests_array + self.skipped_tests_array:
                if test.get_name() == test_name:
                    return test
        return None

    def is_test(self, test_name):
        for test in self.tests_array + self.skipped_tests_array:
            if test.get_name() == test_name:
                return True
        return False

    def get_name(self):
        return self.name

    def __str__(self):
        msg = prettytable.PrettyTable(
            header_style='upper', padding_width=5,
            field_names=['tiers', 'description',
                         'testcases'])
        msg.add_row(
            [self.name, textwrap.fill(self.description, width=40),
             textwrap.fill(' '.join([str(x.get_name(
                 )) for x in self.get_tests()]), width=40)])
        return msg.get_string()


class TestCase():

    def __init__(self, name, enabled, skipped, criteria, blocking,
                 description="", project=""):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        self.name = name
        self.enabled = enabled
        self.skipped = skipped
        self.criteria = criteria
        self.blocking = blocking
        self.description = description
        self.project = project

    def get_name(self):
        return self.name

    def is_enabled(self):
        return self.enabled

    def is_skipped(self):
        return self.skipped

    def get_criteria(self):
        return self.criteria

    def is_blocking(self):
        return self.blocking

    def get_project(self):
        return self.project

    def __str__(self):
        msg = prettytable.PrettyTable(
            header_style='upper', padding_width=5,
            field_names=['test case', 'description', 'criteria'])
        msg.add_row([self.name, textwrap.fill(self.description, width=40),
                     self.criteria])
        return msg.get_string()
