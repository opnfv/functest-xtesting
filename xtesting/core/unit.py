#!/usr/bin/env python

# Copyright (c) 2016 Cable Television Laboratories, Inc. and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define the parent class to run unittest.TestSuite as TestCase."""

from __future__ import division

import logging
import os
import shutil
import subprocess
import time
import unittest

from subunit.run import SubunitTestRunner
import six

from xtesting.core import testcase

__author__ = ("Steven Pisarski <s.pisarski@cablelabs.com>, "
              "Cedric Ollivier <cedric.ollivier@orange.com>")


class Suite(testcase.TestCase):
    """Base model for running unittest.TestSuite."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super(Suite, self).__init__(**kwargs)
        self.res_dir = "/var/lib/xtesting/results/{}".format(self.case_name)
        self.suite = None

    @classmethod
    def generate_stats(cls, stream):
        """Generate stats from subunit stream

        Raises:
            Exception
        """
        stream.seek(0)
        stats = subprocess.Popen(
            ['subunit-stats'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, _ = stats.communicate(stream.read())
        cls.__logger.info("\n\n%s", output)

    def generate_xunit(self, stream):
        """Generate junit report from subunit stream

        Raises:
            Exception
        """
        stream.seek(0)
        with open("{}/results.xml".format(self.res_dir), "w") as xml:
            stats = subprocess.Popen(
                ['subunit2junitxml'], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            output, _ = stats.communicate(stream.read())
            xml.write(output)

    def generate_html(self, stream):
        """Generate html report from subunit stream

        Raises:
            CalledProcessError
        """
        cmd = ['subunit2html', stream, '{}/results.html'.format(self.res_dir)]
        output = subprocess.check_output(cmd)
        self.__logger.debug("\n%s\n\n%s", ' '.join(cmd), output)

    def run(self, **kwargs):
        """Run the test suite.

        It allows running any unittest.TestSuite and getting its
        execution status.

        By default, it runs the suite defined as instance attribute.
        It can be overriden by passing name as arg. It must
        conform with TestLoader.loadTestsFromName().

        It sets the following attributes required to push the results
        to DB:

            * result,
            * start_time,
            * stop_time,
            * details.

        Args:
            kwargs: Arbitrary keyword arguments.

        Return:
            TestCase.EX_OK if any TestSuite has been run
            TestCase.EX_RUN_ERROR otherwise.
        """
        try:
            name = kwargs["name"]
            try:
                self.suite = unittest.TestLoader().loadTestsFromName(name)
            except ImportError:
                self.__logger.error("Can not import %s", name)
                return testcase.TestCase.EX_RUN_ERROR
        except KeyError:
            pass
        try:
            assert self.suite
            self.start_time = time.time()
            if not os.path.isdir(self.res_dir):
                os.makedirs(self.res_dir)
            stream = six.StringIO()
            result = SubunitTestRunner(
                stream=stream, verbosity=2).run(self.suite).decorated
            self.generate_stats(stream)
            self.generate_xunit(stream)
            with open('{}/subunit_stream'.format(self.res_dir), 'w') as subfd:
                stream.seek(0)
                shutil.copyfileobj(stream, subfd)
            self.generate_html('{}/subunit_stream'.format(self.res_dir))
            self.stop_time = time.time()
            self.details = {
                "testsRun": result.testsRun,
                "failures": len(result.failures),
                "errors": len(result.errors)}
            self.result = 100 * (
                (result.testsRun - (len(result.failures) +
                                    len(result.errors))) /
                result.testsRun)
            return testcase.TestCase.EX_OK
        except AssertionError:
            self.__logger.error("No suite is defined")
            return testcase.TestCase.EX_RUN_ERROR
        except ZeroDivisionError:
            self.__logger.error("No test has been run")
            return testcase.TestCase.EX_RUN_ERROR
        except Exception:  # pylint: disable=broad-except
            self.__logger.exception("something wrong occurs")
            return testcase.TestCase.EX_RUN_ERROR
