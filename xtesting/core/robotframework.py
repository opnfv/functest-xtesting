#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define classes required to run any Robot suites."""

from __future__ import division

import logging
import os

from io import StringIO
import robot.api
from robot.errors import RobotError
from robot.reporting import resultwriter
import robot.run
from robot.utils.robottime import timestamp_to_secs

from xtesting.core import testcase

__author__ = "Cedric Ollivier <cedric.ollivier@orange.com>"


class ResultVisitor(robot.api.ResultVisitor):
    """Visitor to get result details."""

    def __init__(self):
        self._data = []

    def visit_test(self, test):
        output = {}
        output['name'] = test.name
        output['parent'] = test.parent.name
        output['status'] = test.status
        output['starttime'] = test.starttime
        output['endtime'] = test.endtime
        output['text'] = test.message
        output['elapsedtime'] = test.elapsedtime
        self._data.append(output)

    def get_data(self):
        """Get the details of the result."""
        return self._data


class RobotFramework(testcase.TestCase):
    """RobotFramework runner."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_file = os.path.join(self.res_dir, 'output.xml')

    def parse_results(self):
        """Parse output.xml and get the details in it."""
        result = robot.api.ExecutionResult(self.xml_file)
        visitor = ResultVisitor()
        result.visit(visitor)
        try:
            self.result = 100 * (
                result.suite.statistics.passed /
                result.suite.statistics.total)
        except ZeroDivisionError:
            self.__logger.error("No test has been run")
        self.start_time = timestamp_to_secs(result.suite.starttime)
        self.stop_time = timestamp_to_secs(result.suite.endtime)
        self.details = {}
        self.details['description'] = result.suite.name
        self.details['tests'] = visitor.get_data()

    def generate_report(self):
        """Generate html and xunit outputs"""
        result = robot.api.ExecutionResult(self.xml_file)
        writer = resultwriter.ResultWriter(result)
        return writer.write_results(
            report=f'{self.res_dir}/report.html',
            log=f'{self.res_dir}/log.html',
            xunit=f'{self.res_dir}/xunit.xml')

    def run(self, **kwargs):
        """Run the RobotFramework suites

        Here are the steps:
           * create the output directories if required,
           * get the results in output.xml,
           * delete temporary files.

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            EX_OK if all suites ran well.
            EX_RUN_ERROR otherwise.
        """
        try:
            suites = kwargs["suites"]
            variable = kwargs.get("variable", [])
            variablefile = kwargs.get("variablefile", [])
            include = kwargs.get("include", [])
        except KeyError:
            self.__logger.exception("Mandatory args were not passed")
            return self.EX_RUN_ERROR
        if not os.path.exists(self.res_dir):
            try:
                os.makedirs(self.res_dir)
            except Exception:  # pylint: disable=broad-except
                self.__logger.exception("Cannot create %s", self.res_dir)
                return self.EX_RUN_ERROR
        stream = StringIO()
        robot.run(*suites, variable=variable, variablefile=variablefile,
                  include=include, output=self.xml_file, log='NONE',
                  report='NONE', stdout=stream)
        self.__logger.info("\n%s", stream.getvalue())
        try:
            self.parse_results()
            self.__logger.info("Results were successfully parsed")
            self.generate_report()
            self.__logger.info("Results were successfully generated")
        except RobotError as ex:
            self.__logger.error("Run suites before publishing: %s", ex.message)
            return self.EX_RUN_ERROR
        except Exception:  # pylint: disable=broad-except
            self.__logger.exception("Cannot parse results")
            return self.EX_RUN_ERROR
        return self.EX_OK
