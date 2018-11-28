#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import logging
import subprocess
import unittest

import mock

from xtesting.core import feature
from xtesting.core import testcase


class FakeTestCase(feature.Feature):

    def execute(self, **kwargs):
        pass


class AbstractFeatureTesting(unittest.TestCase):

    def test_run_unimplemented(self):
        with self.assertRaises(TypeError):
            feature.Feature(case_name="feature", project_name="xtesting")


class FeatureTestingBase(unittest.TestCase):

    _case_name = "foo"
    _project_name = "bar"
    _repo = "dir_repo_bar"
    _cmd = "run_bar_tests.py"
    _output_file = '/var/lib/xtesting/results/foo.log'
    feature = None

    @mock.patch('time.time', side_effect=[1, 2])
    def _test_run(self, status, mock_method=None):
        self.assertEqual(self.feature.run(cmd=self._cmd), status)
        if status == testcase.TestCase.EX_OK:
            self.assertEqual(self.feature.result, 100)
        else:
            self.assertEqual(self.feature.result, 0)
        mock_method.assert_has_calls([mock.call(), mock.call()])
        self.assertEqual(self.feature.start_time, 1)
        self.assertEqual(self.feature.stop_time, 2)


class FeatureTesting(FeatureTestingBase):

    def setUp(self):
        # logging must be disabled else it calls time.time()
        # what will break these unit tests.
        logging.disable(logging.CRITICAL)
        with mock.patch('six.moves.builtins.open'):
            self.feature = FakeTestCase(
                project_name=self._project_name, case_name=self._case_name)

    def test_run_exc(self):
        # pylint: disable=bad-continuation
        with mock.patch.object(
                self.feature, 'execute',
                side_effect=Exception) as mock_method:
            self._test_run(testcase.TestCase.EX_RUN_ERROR)
            mock_method.assert_called_once_with(cmd=self._cmd)

    def test_run(self):
        self._test_run(testcase.TestCase.EX_RUN_ERROR)


class BashFeatureTesting(FeatureTestingBase):

    def setUp(self):
        # logging must be disabled else it calls time.time()
        # what will break these unit tests.
        logging.disable(logging.CRITICAL)
        with mock.patch('six.moves.builtins.open'):
            self.feature = feature.BashFeature(
                project_name=self._project_name, case_name=self._case_name)

    @mock.patch('subprocess.check_call')
    def test_run_no_cmd(self, mock_subproc):
        delattr(FeatureTesting, "_cmd")
        self.assertEqual(
            self.feature.run(), testcase.TestCase.EX_RUN_ERROR)
        mock_subproc.assert_not_called()

    @mock.patch('subprocess.check_call',
                side_effect=subprocess.CalledProcessError)
    def test_run_ko(self, mock_subproc):
        setattr(FeatureTesting, "_cmd", "run_bar_tests.py")
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run(testcase.TestCase.EX_RUN_ERROR)
        mopen.assert_called_once_with(self._output_file, "w+")
        mock_subproc.assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)

    @mock.patch('subprocess.check_call')
    def test_run(self, mock_subproc):
        setattr(FeatureTesting, "_cmd", "run_bar_tests.py")
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run(testcase.TestCase.EX_OK)
        mopen.assert_called_once_with(self._output_file, "w+")
        mock_subproc.assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
