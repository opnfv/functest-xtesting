#!/usr/bin/env python

# Copyright (c) 2021 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Implement a Xtesting driver to run any Ansible playbook."""

import logging
import os
import shutil
import time

import ansible_runner

from xtesting.core import testcase


class Ansible(testcase.TestCase):
    """Class designed to run any Ansible playbook via ansible-runner."""

    __logger = logging.getLogger(__name__)

    def check_requirements(self):
        """Check if ansible-playbook is in $PATH"""
        self.is_skipped = not shutil.which("ansible-playbook")
        if self.is_skipped:
            self.__logger.warning("ansible-playbook is missing")

    def run(self, **kwargs):
        """ Wrap ansible_runner.interface.run()

        It calls ansible_runner.interface.run() by converting the testcase
        description data to kwargs. It only overrides quiet and artifact_dir to
        implement the Xtesting behavior.

        Following the playbook logic, criteria is considered as boolean
        whatever the value set in testcases.yaml.

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            EX_OK if the playbook ran well.
            EX_RUN_ERROR otherwise.
        """
        status = self.EX_RUN_ERROR
        self.start_time = time.time()
        if ("private_data_dir" in kwargs and
                os.path.isdir(kwargs['private_data_dir'])):
            try:
                if not os.path.exists(self.res_dir):
                    os.makedirs(self.res_dir)
                if "quiet" not in kwargs:
                    kwargs["quiet"] = True
                kwargs["artifact_dir"] = self.res_dir
                runner = ansible_runner.run(**kwargs)
                self.details = runner.stats
                if runner.rc == 0:
                    self.result = 100
                status = self.EX_OK
            except Exception:  # pylint: # pylint: disable=broad-except
                self.__logger.exception("Cannot execute the playbook")
        else:
            self.__logger.error(
                "Please set a relevant private_data_dir in testcases.yaml")
        self.stop_time = time.time()
        return status
