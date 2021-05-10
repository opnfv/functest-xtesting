#!/usr/bin/env python

# Copyright (c) 2016 Ericsson AB and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

""" The entry of running tests:
1) Parses xtesting/ci/testcases.yaml to check which testcase(s) to be run
2) Execute the common operations on every testcase (run, push results to db...)
3) Return the right status code
"""

import argparse
import errno
import logging
import logging.config
import os
import re
import sys
import textwrap

import enum
import pkg_resources
import prettytable
import six
from stevedore import driver
import yaml

from xtesting.ci import tier_builder
from xtesting.core import testcase
from xtesting.utils import constants
from xtesting.utils import env

LOGGER = logging.getLogger('xtesting.ci.run_tests')


class Result(enum.Enum):
    """The overall result in enumerated type"""
    # pylint: disable=too-few-public-methods
    EX_OK = os.EX_OK
    EX_ERROR = -1


class BlockingTestFailed(Exception):
    """Exception when the blocking test fails"""


class RunTestsParser():
    """Parser to run tests"""
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-t", "--test", dest="test", action='store',
                                 help="Test case or tier (group of tests) "
                                 "to be executed. It will run all the test "
                                 "if not specified.")
        self.parser.add_argument("-n", "--noclean", help="Do not clean "
                                 "OpenStack resources after running each "
                                 "test (default=false).",
                                 action="store_true")
        self.parser.add_argument("-r", "--report", help="Push results to "
                                 "database (default=false).",
                                 action="store_true")
        self.parser.add_argument("-p", "--push", help="Push artifacts to "
                                 "S3 repository (default=false).",
                                 action="store_true")

    def parse_args(self, argv=None):
        """Parse arguments.

        It can call sys.exit if arguments are incorrect.

        Returns:
            the arguments from cmdline
        """
        return vars(self.parser.parse_args(argv))


class Runner():
    """Runner class"""

    def __init__(self):
        self.executed_test_cases = {}
        self.overall_result = Result.EX_OK
        self.clean_flag = True
        self.report_flag = False
        self.push_flag = False
        self.tiers = tier_builder.TierBuilder(
            pkg_resources.resource_filename('xtesting', 'ci/testcases.yaml'))

    @staticmethod
    def source_envfile(rc_file=constants.ENV_FILE):
        """Source the env file passed as arg"""
        if not os.path.isfile(rc_file):
            LOGGER.debug("No env file %s found", rc_file)
            return
        with open(rc_file, "r") as rcfd:
            for line in rcfd:
                var = (line.rstrip('"\n').replace('export ', '').split(
                    "=") if re.search(r'(.*)=(.*)', line) else None)
                # The two next lines should be modified as soon as rc_file
                # conforms with common rules. Be aware that it could induce
                # issues if value starts with '
                if var:
                    key = re.sub(r'^["\' ]*|[ \'"]*$', '', var[0])
                    value = re.sub(r'^["\' ]*|[ \'"]*$', '', "".join(var[1:]))
                    os.environ[key] = value
            rcfd.seek(0, 0)
            LOGGER.debug("Sourcing env file %s\n\n%s", rc_file, rcfd.read())

    @staticmethod
    def get_dict_by_test(testname):
        # pylint: disable=bad-continuation,missing-docstring
        with open(pkg_resources.resource_filename(
                'xtesting', 'ci/testcases.yaml')) as tyaml:
            testcases_yaml = yaml.safe_load(tyaml)
        for dic_tier in testcases_yaml.get("tiers"):
            for dic_testcase in dic_tier['testcases']:
                if dic_testcase['case_name'] == testname:
                    return dic_testcase
        LOGGER.error('Project %s is not defined in testcases.yaml', testname)
        return None

    @staticmethod
    def get_run_dict(testname):
        """Obtain the 'run' block of the testcase from testcases.yaml"""
        try:
            dic_testcase = Runner.get_dict_by_test(testname)
            if not dic_testcase:
                LOGGER.error("Cannot get %s's config options", testname)
            elif 'run' in dic_testcase:
                return dic_testcase['run']
            return None
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Cannot get %s's config options", testname)
            return None

    def run_test(self, test):
        """Run one test case"""
        if not test.is_enabled() or test.is_skipped():
            msg = prettytable.PrettyTable(
                header_style='upper', padding_width=5,
                field_names=['test case', 'project', 'duration',
                             'result'])
            msg.add_row([test.get_name(), test.get_project(), "00:00", "SKIP"])
            LOGGER.info("Test result:\n\n%s\n", msg)
            return testcase.TestCase.EX_TESTCASE_SKIPPED
        result = testcase.TestCase.EX_TESTCASE_FAILED
        run_dict = self.get_run_dict(test.get_name())
        if run_dict:
            try:
                LOGGER.info("Loading test case '%s'...", test.get_name())
                test_dict = Runner.get_dict_by_test(test.get_name())
                test_case = driver.DriverManager(
                    namespace='xtesting.testcase',
                    name=run_dict['name'],
                    invoke_on_load=True,
                    invoke_kwds=test_dict).driver
                self.executed_test_cases[test.get_name()] = test_case
                test_case.check_requirements()
                if test_case.is_skipped:
                    LOGGER.info("Skipping test case '%s'...", test.get_name())
                    LOGGER.info("Test result:\n\n%s\n", test_case)
                    return testcase.TestCase.EX_TESTCASE_SKIPPED
                LOGGER.info("Running test case '%s'...", test.get_name())
                try:
                    kwargs = run_dict['args']
                    test_case.run(**kwargs)
                except KeyError:
                    test_case.run()
                result = test_case.is_successful()
                LOGGER.info("Test result:\n\n%s\n", test_case)
                if self.clean_flag:
                    test_case.clean()
                if self.push_flag:
                    test_case.publish_artifacts()
                if self.report_flag:
                    test_case.push_to_db()
            except ImportError:
                LOGGER.exception("Cannot import module %s", run_dict['module'])
            except AttributeError:
                LOGGER.exception("Cannot get class %s", run_dict['class'])
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception(
                    "\n\nPlease fix the testcase %s.\n"
                    "All exceptions should be caught by the testcase instead!"
                    "\n\n",
                    test.get_name())
        else:
            raise Exception("Cannot import the class for the test case.")
        return result

    def run_tier(self, tier):
        """Run one tier"""
        tests = tier.get_tests()
        if not tests:
            LOGGER.info("There are no supported test cases in this tier "
                        "for the given scenario")
            self.overall_result = Result.EX_ERROR
        else:
            for test in tests:
                self.run_test(test)
                test_case = self.executed_test_cases[test.get_name()]
                if test_case.is_successful() == test_case.EX_TESTCASE_FAILED:
                    LOGGER.error("The test case '%s' failed.", test.get_name())
                    self.overall_result = Result.EX_ERROR
                    if test.is_blocking():
                        raise BlockingTestFailed(
                            "The test case {} failed and is blocking".format(
                                test.get_name()))
        return self.overall_result

    def run_all(self):
        """Run all available testcases"""
        tiers_to_run = []
        msg = prettytable.PrettyTable(
            header_style='upper', padding_width=5,
            field_names=['tiers', 'description', 'testcases'])
        for tier in self.tiers.get_tiers():
            if tier.get_tests():
                tiers_to_run.append(tier)
                msg.add_row([tier.get_name(),
                             textwrap.fill(tier.description, width=40),
                             textwrap.fill(' '.join([str(x.get_name(
                                 )) for x in tier.get_tests()]), width=40)])
        LOGGER.info("TESTS TO BE EXECUTED:\n\n%s\n", msg)
        for tier in tiers_to_run:
            self.run_tier(tier)

    def main(self, **kwargs):  # pylint: disable=too-many-branches
        """Entry point of class Runner"""
        if 'noclean' in kwargs:
            self.clean_flag = not kwargs['noclean']
        if 'report' in kwargs:
            self.report_flag = kwargs['report']
        if 'push' in kwargs:
            self.push_flag = kwargs['push']
        try:
            LOGGER.info("Deployment description:\n\n%s\n", env.string())
            self.source_envfile()
            if 'test' in kwargs:
                LOGGER.debug("Test args: %s", kwargs['test'])
                if self.tiers.get_tier(kwargs['test']):
                    self.run_tier(self.tiers.get_tier(kwargs['test']))
                elif self.tiers.get_test(kwargs['test']):
                    result = self.run_test(
                        self.tiers.get_test(kwargs['test']))
                    if result == testcase.TestCase.EX_TESTCASE_FAILED:
                        LOGGER.error("The test case '%s' failed.",
                                     kwargs['test'])
                        self.overall_result = Result.EX_ERROR
                elif kwargs['test'] == "all":
                    self.run_all()
                else:
                    LOGGER.error("Unknown test case or tier '%s', or not "
                                 "supported by the given scenario '%s'.",
                                 kwargs['test'],
                                 env.get('DEPLOY_SCENARIO'))
                    LOGGER.debug("Available tiers are:\n\n%s",
                                 self.tiers)
                    return Result.EX_ERROR
            else:
                self.run_all()
        except BlockingTestFailed:
            pass
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Failures when running testcase(s)")
            self.overall_result = Result.EX_ERROR
        if not self.tiers.get_test(kwargs['test']):
            self.summary(self.tiers.get_tier(kwargs['test']))
        LOGGER.info("Execution exit value: %s", self.overall_result)
        return self.overall_result

    def summary(self, tier=None):
        """To generate xtesting report showing the overall results"""
        msg = prettytable.PrettyTable(
            header_style='upper', padding_width=5,
            field_names=['test case', 'project', 'tier',
                         'duration', 'result'])
        tiers = [tier] if tier else self.tiers.get_tiers()
        for each_tier in tiers:
            for test in each_tier.get_tests():
                try:
                    test_case = self.executed_test_cases[test.get_name()]
                except KeyError:
                    msg.add_row([test.get_name(), test.get_project(),
                                 each_tier.get_name(), "00:00", "SKIP"])
                else:
                    if test_case.is_skipped:
                        result = 'SKIP'
                    else:
                        result = 'PASS' if(test_case.is_successful(
                            ) == test_case.EX_OK) else 'FAIL'
                    msg.add_row(
                        [test_case.case_name, test_case.project_name,
                         self.tiers.get_tier_name(test_case.case_name),
                         test_case.get_duration(), result])
            for test in each_tier.get_skipped_test():
                msg.add_row([test.get_name(), test.get_project(),
                             each_tier.get_name(), "00:00", "SKIP"])
        LOGGER.info("Xtesting report:\n\n%s\n", msg)


def main():
    """Entry point"""
    try:
        os.makedirs(constants.RESULTS_DIR)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            six.print_("{} {}".format("Cannot create", constants.RESULTS_DIR))
            return testcase.TestCase.EX_RUN_ERROR
    if env.get('DEBUG').lower() == 'true':
        logging.config.fileConfig(pkg_resources.resource_filename(
            'xtesting', constants.DEBUG_INI_PATH))
    else:
        logging.config.fileConfig(pkg_resources.resource_filename(
            'xtesting', constants.INI_PATH))
    logging.captureWarnings(True)
    parser = RunTestsParser()
    args = parser.parse_args(sys.argv[1:])
    runner = Runner()
    return runner.main(**args).value
