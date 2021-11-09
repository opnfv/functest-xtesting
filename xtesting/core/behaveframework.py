#!/usr/bin/env python

# Copyright (c) 2019 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define classes required to run any Behave test suites."""

from __future__ import division

import logging
import os
import time

import json

from behave.__main__ import main as behave_main

from xtesting.core import testcase

__author__ = "Deepak Chandella <deepak.chandella@orange.com>"


class BehaveFramework(testcase.TestCase):
    """BehaveFramework runner."""
    # pylint: disable=too-many-instance-attributes

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.json_file = os.path.join(self.res_dir, 'output.json')
        self.total_tests = 0
        self.pass_tests = 0
        self.fail_tests = 0
        self.skip_tests = 0
        self.response = None

    def parse_results(self):
        """Parse output.json and get the details in it."""
        with open(self.json_file, encoding='utf-8') as stream_:
            self.response = json.load(stream_)
            if self.response:
                self.total_tests = len(self.response)
            for item in self.response:
                if item['status'] == 'passed':
                    self.pass_tests += 1
                elif item['status'] == 'failed':
                    self.fail_tests += 1
                elif item['status'] == 'skipped':
                    self.skip_tests += 1
            self.result = 100 * (
                self.pass_tests / self.total_tests)
            self.details = {}
            self.details['total_tests'] = self.total_tests
            self.details['pass_tests'] = self.pass_tests
            self.details['fail_tests'] = self.fail_tests
            self.details['skip_tests'] = self.skip_tests
            self.details['tests'] = self.response

    def run(self, **kwargs):
        """Run the BehaveFramework feature files

        Here are the steps:
           * create the output directories if required,
           * run behave features with parameters
           * get the results in output.json,

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            EX_OK if all suites ran well.
            EX_RUN_ERROR otherwise.
        """
        try:
            suites = kwargs["suites"]
        except KeyError:
            self.__logger.exception("Mandatory args were not passed")
            return self.EX_RUN_ERROR
        if not os.path.exists(self.res_dir):
            try:
                os.makedirs(self.res_dir)
            except Exception:  # pylint: disable=broad-except
                self.__logger.exception("Cannot create %s", self.res_dir)
                return self.EX_RUN_ERROR
        config = ['--junit', f'--junit-directory={self.res_dir}',
                  '--format=json', f'--outfile={self.json_file}']
        html_file = os.path.join(self.res_dir, 'output.html')
        config += ['--format=behave_html_formatter:HTMLFormatter',
                   f'--outfile={html_file}']
        if kwargs.get("tags", False):
            config += ['--tags='+','.join(kwargs.get("tags", []))]
        if kwargs.get("console", False):
            config += ['--format=pretty', '--outfile=-']
        for feature in suites:
            config.append(feature)
        self.start_time = time.time()
        behave_main(config)
        self.stop_time = time.time()

        try:
            self.parse_results()
            self.__logger.info("Results were successfully parsed")
        except Exception:  # pylint: disable=broad-except
            self.__logger.exception("Cannot parse results")
            return self.EX_RUN_ERROR
        return self.EX_OK
