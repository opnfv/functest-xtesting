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
import six

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
    _output_file = '/var/lib/xtesting/results/foo/foo.log'
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

    @mock.patch('time.time', side_effect=[1, 2])
    def _test_run_console(self, console, status, mock_method=None):
        self.assertEqual(
            self.feature.run(cmd=self._cmd, console=console), status)
        self.assertEqual(self.feature.result, 100)
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

    @mock.patch('subprocess.Popen')
    def test_run_no_cmd(self, mock_subproc):
        self.assertEqual(
            self.feature.run(), testcase.TestCase.EX_RUN_ERROR)
        mock_subproc.assert_not_called()

    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('subprocess.Popen',
                side_effect=subprocess.CalledProcessError(0, '', ''))
    def test_run_ko1(self, *args):
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run(testcase.TestCase.EX_RUN_ERROR)
        mopen.assert_called_once_with(self._output_file, "w")
        args[0].assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)
        args[1].assert_called_once_with(self.feature.res_dir)

    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_run_ko2(self, *args):
        stream = six.StringIO()
        stream.write("foo")
        stream.seek(0)
        attrs = {'return_value.stdout': stream, 'return_value.returncode': 1}
        args[0].configure_mock(**attrs)
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run(testcase.TestCase.EX_RUN_ERROR)
        self.assertIn(mock.call(self._output_file, 'w'), mopen.mock_calls)
        self.assertIn(mock.call(self._output_file, 'r'), mopen.mock_calls)
        args[0].assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)
        args[1].assert_called_once_with(self.feature.res_dir)

    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_run1(self, *args):
        stream = six.StringIO()
        stream.write("foo")
        stream.seek(0)
        attrs = {'return_value.stdout': stream, 'return_value.returncode': 0}
        args[0].configure_mock(**attrs)
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run(testcase.TestCase.EX_OK)
        self.assertIn(mock.call(self._output_file, 'w'), mopen.mock_calls)
        self.assertIn(mock.call(self._output_file, 'r'), mopen.mock_calls)
        args[0].assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)
        args[1].assert_called_once_with(self.feature.res_dir)

    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_run2(self, *args):
        stream = six.StringIO()
        stream.write("foo")
        stream.seek(0)
        attrs = {'return_value.stdout': stream, 'return_value.returncode': 0}
        args[0].configure_mock(**attrs)
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run_console(True, testcase.TestCase.EX_OK)
        self.assertIn(mock.call(self._output_file, 'w'), mopen.mock_calls)
        self.assertIn(mock.call(self._output_file, 'r'), mopen.mock_calls)
        args[0].assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)
        args[1].assert_called_once_with(self.feature.res_dir)

    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_run3(self, *args):
        stream = six.StringIO()
        stream.write("foo")
        stream.seek(0)
        attrs = {'return_value.stdout': stream, 'return_value.returncode': 0}
        args[0].configure_mock(**attrs)
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run_console(False, testcase.TestCase.EX_OK)
        self.assertIn(mock.call(self._output_file, 'w'), mopen.mock_calls)
        self.assertIn(mock.call(self._output_file, 'r'), mopen.mock_calls)
        args[0].assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)
        args[1].assert_called_once_with(self.feature.res_dir)

    @mock.patch('os.makedirs')
    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('subprocess.Popen')
    def test_run4(self, *args):
        stream = six.StringIO()
        stream.write("foo")
        stream.seek(0)
        attrs = {'return_value.stdout': stream, 'return_value.returncode': 0}
        args[0].configure_mock(**attrs)
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as mopen:
            self._test_run_console(False, testcase.TestCase.EX_OK)
        self.assertIn(mock.call(self._output_file, 'w'), mopen.mock_calls)
        self.assertIn(mock.call(self._output_file, 'r'), mopen.mock_calls)
        args[0].assert_called_once_with(
            self._cmd, shell=True, stderr=mock.ANY, stdout=mock.ANY)
        args[1].assert_called_once_with(self.feature.res_dir)
        args[2].assert_called_once_with(self.feature.res_dir)


if __name__ == "__main__":
    unittest.main(verbosity=2)
