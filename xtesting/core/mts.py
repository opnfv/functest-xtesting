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

__author__ = ("Vincent Mahe <v.mahe@orange.com>, "
              "Cedric Ollivier <cedric.ollivier@orange.com>")


class MTSLauncher(testcase.TestCase):
    """Class designed to run any bash command."""

    __logger = logging.getLogger(__name__)
    mts_install_dir = "/opt/mts/bin"

    def __init__(self, **kwargs):
        super(MTSLauncher, self).__init__(**kwargs)
        self.result_file = "{}/{}.log".format(self.res_dir, self.case_name)
        self.mts_stats_dir = os.path.join(self.res_dir, 'mts_stats_report')
        # Need to end path with a separator because of a bug in MTS.
        self.mts_logs_dir = os.path.join(self.res_dir,
                                         'mts_logs' + os.path.sep)

    def execute(self, **kwargs):
        """Execute the cmd passed as arg

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            0 if cmd returns 0,
            -1 otherwise.
        """
        try:
            six.print_("Hello World MTS Launcher")
            suite = kwargs["suite"]
            console = kwargs["console"] if "console" in kwargs else False
            log_level = kwargs["log_level"] if "log_level" in kwargs else "INFO"
            store_method = kwargs[
                "store_method"] if "store_method" in kwargs else "FILE"
            # java_memory = kwargs["java_memory"] if "java_memory" in kwargs else 1024
            cmd = "./startCmd.sh {} -sequential -levelLog:{} -storageLog:{} -config:stats.REPORT_DIRECTORY+{} -config:logs.STORAGE_DIRECTORY+{} -genReport:true -showRep:false".format(
                suite, log_level, store_method, self.mts_stats_dir, self.mts_logs_dir)
            if not os.path.isdir(self.res_dir):
                os.makedirs(self.res_dir)
            if not os.path.isdir(self.mts_stats_dir):
                os.makedirs(self.mts_stats_dir)
            if not os.path.isdir(self.mts_logs_dir):
                os.makedirs(self.mts_logs_dir)
            with open(self.result_file, 'w') as f_stdout:
                self.__logger.info("Calling %s", cmd)
                process = subprocess.Popen(cmd,
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           cwd=self.mts_install_dir)
                for line in iter(process.stdout.readline, b''):
                    if console:
                        sys.stdout.write(line.decode("utf-8"))
                    f_stdout.write(line.decode("utf-8"))
                process.wait()
            with open(self.result_file, 'r') as f_stdin:
                self.__logger.debug("$ %s\n%s", cmd, f_stdin.read().rstrip())
            return process.returncode
        except KeyError:
            self.__logger.error("Please give cmd as arg. kwargs: %s", kwargs)
        return -1

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
