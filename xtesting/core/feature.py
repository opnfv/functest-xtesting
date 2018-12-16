#!/usr/bin/env python

# Copyright (c) 2016 ZTE Corp and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define the parent classes of all Xtesting Features.

Feature is considered as TestCase offered by Third-party. It offers
helpers to run any python method or any bash command.
"""

import abc
import logging
import os
import subprocess
import sys
import time

import six
from xtesting.core import testcase

__author__ = ("Serena Feng <feng.xiaowei@zte.com.cn>, "
              "Cedric Ollivier <cedric.ollivier@orange.com>")


@six.add_metaclass(abc.ABCMeta)
class Feature(testcase.TestCase):
    """Base model for single feature."""

    __logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def execute(self, **kwargs):
        """Execute the Python method.

        The subclasses must override the default implementation which
        is false on purpose.

        The new implementation must return 0 if success or anything
        else if failure.

        Args:
            kwargs: Arbitrary keyword arguments.
        """

    def run(self, **kwargs):
        """Run the feature.

        It allows executing any Python method by calling execute().

        It sets the following attributes required to push the results
        to DB:

            * result,
            * start_time,
            * stop_time.

        It doesn't fulfill details when pushing the results to the DB.

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            TestCase.EX_OK if execute() returns 0,
            TestCase.EX_RUN_ERROR otherwise.
        """
        self.start_time = time.time()
        exit_code = testcase.TestCase.EX_RUN_ERROR
        self.result = 0
        try:
            if self.execute(**kwargs) == 0:
                exit_code = testcase.TestCase.EX_OK
                self.result = 100
        except Exception:  # pylint: disable=broad-except
            self.__logger.exception("%s FAILED", self.project_name)
        self.stop_time = time.time()
        return exit_code


class BashFeature(Feature):
    """Class designed to run any bash command."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super(BashFeature, self).__init__(**kwargs)
        self.res_dir = "/var/lib/xtesting/results/{}".format(self.case_name)
        self.result_file = "{}/{}.log".format(self.res_dir, self.case_name)

    def execute(self, **kwargs):
        """Execute the cmd passed as arg

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            0 if cmd returns 0,
            -1 otherwise.
        """
        try:
            cmd = kwargs["cmd"]
            console = kwargs["console"] if "console" in kwargs else False
            if not os.path.isdir(self.res_dir):
                os.makedirs(self.res_dir)
            with open(self.result_file, 'w') as f_stdout:
                self.__logger.info("Calling %s", cmd)
                process = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
                for line in iter(process.stdout.readline, ''):
                    if console:
                        sys.stdout.write(line)
                    f_stdout.write(line)
                process.wait()
            with open(self.result_file, 'r') as f_stdin:
                self.__logger.debug("$ %s\n%s", cmd, f_stdin.read().rstrip())
            return process.returncode
        except KeyError:
            self.__logger.error("Please give cmd as arg. kwargs: %s", kwargs)
        return -1
