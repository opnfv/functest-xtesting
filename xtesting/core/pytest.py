#!/usr/bin/env python

# Copyright (c) 2023 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define classes required to run any Pytest suites."""

import contextlib
import io
import logging
import time

import pytest

from xtesting.core import testcase


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect all Pytest results"""
    # pylint: disable=unused-argument
    yreport = yield
    report = yreport.get_result()
    if report.when == 'call':
        test = {"name": report.nodeid, "status": report.outcome.upper()}
        if report.passed:
            Pytest.passed += 1
        elif report.failed:
            Pytest.failed += 1
            test['failure'] = report.longreprtext
        Pytest.tests.append(test)


class Pytest(testcase.TestCase):

    """Pytest driver

    The pytest driver can be used on every test set written for pytest.
    Given a pytest package that is launched with the command:

    .. code-block:: shell

        pytest --opt1 arg1 --opt2 testdir

    it can be executed by xtesting with the following testcase.yaml:

    .. code-block:: yaml

        run:
          name: pytest
          args:
            opt1: arg1
            opt2: arg2
    """

    __logger = logging.getLogger(__name__)
    tests = []
    passed = 0
    failed = 0

    def run(self, **kwargs):
        # parsing args
        #  - 'dir' is mandatory
        #  - 'options' is an optional list or a dict flatten to a list
        status = self.EX_RUN_ERROR
        self.start_time = time.time()
        try:
            pydir = kwargs.pop('dir')
            options = kwargs.pop('options', {})
            options['html'] = f'{self.res_dir}/results.html'
            options['junitxml'] = f'{self.res_dir}/results.xml'
            if 'tb' not in options:
                options['tb'] = 'no'
            options = [
                str(item) for opt in zip(
                    [f'--{k}' if len(str(k)) > 1 else
                        f'-{k}' for k in options.keys()],
                    options.values())
                for item in opt if item is not None]
            with contextlib.redirect_stdout(io.StringIO()) as output:
                pytest.main(
                    args=[pydir] + ['-p', __name__] + options)
            with open(f'{self.res_dir}/stdout.log',
                      'w', encoding='utf-8') as output_file:
                output_file.write(output.getvalue())
            self.__logger.info(
                "\n\n %s \n",
                output.getvalue().splitlines()[-1].replace('=', ''))
            self.details = Pytest.tests
            if Pytest.passed + Pytest.failed:
                self.result = Pytest.passed / (
                    Pytest.passed + Pytest.failed) * 100
            status = self.EX_OK
        except Exception:  # pylint: # pylint: disable=broad-except
            self.__logger.exception("Cannot execute pytest")
        self.stop_time = time.time()
        return status
