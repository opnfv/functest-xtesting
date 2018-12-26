#!/usr/bin/env python

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

from xtesting.core import unit
from xtesting.core import testcase


class SuiteTesting(unittest.TestCase):

    def setUp(self):
        self.psrunner = unit.Suite(case_name="unit")
        self.psrunner.suite = "foo"

    @mock.patch('subprocess.Popen', side_effect=Exception)
    def test_generate_stats_ko(self, *args):
        stream = six.StringIO()
        with self.assertRaises(Exception):
            self.psrunner.generate_stats(stream)
        args[0].assert_called_once_with(
            ['subunit-stats'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    @mock.patch('subprocess.Popen',
                return_value=mock.Mock(
                    communicate=mock.Mock(return_value=("foo", "bar"))))
    def test_generate_stats_ok(self, *args):
        stream = six.StringIO()
        self.psrunner.generate_stats(stream)
        args[0].assert_called_once_with(
            ['subunit-stats'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    @mock.patch('six.moves.builtins.open', mock.mock_open())
    @mock.patch('subprocess.Popen', side_effect=Exception)
    def test_generate_xunit_ko(self, *args):
        stream = six.StringIO()
        with self.assertRaises(Exception), \
                mock.patch('six.moves.builtins.open',
                           mock.mock_open()) as mock_open:
            self.psrunner.generate_xunit(stream)
        args[0].assert_called_once_with(
            ['subunit2junitxml'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        mock_open.assert_called_once_with(
            '{}/results.xml'.format(self.psrunner.res_dir), 'w')

    @mock.patch('subprocess.Popen',
                return_value=mock.Mock(
                    communicate=mock.Mock(return_value=("foo", "bar"))))
    def test_generate_xunit_ok(self, *args):
        stream = six.StringIO()
        with mock.patch('six.moves.builtins.open',
                        mock.mock_open()) as mock_open:
            self.psrunner.generate_xunit(stream)
        args[0].assert_called_once_with(
            ['subunit2junitxml'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        mock_open.assert_called_once_with(
            '{}/results.xml'.format(self.psrunner.res_dir), 'w')

    @mock.patch('subprocess.check_output', side_effect=Exception)
    def test_generate_html_ko(self, *args):
        stream = "foo"
        with self.assertRaises(Exception):
            self.psrunner.generate_html(stream)
        args[0].assert_called_once_with(
            ['subunit2html', stream,
             '{}/results.html'.format(self.psrunner.res_dir)])

    @mock.patch('subprocess.check_output')
    def test_generate_html_ok(self, *args):
        stream = "foo"
        self.psrunner.generate_html(stream)
        args[0].assert_called_once_with(
            ['subunit2html', stream,
             '{}/results.html'.format(self.psrunner.res_dir)])

    @mock.patch('xtesting.core.unit.Suite.generate_html')
    @mock.patch('xtesting.core.unit.Suite.generate_xunit')
    @mock.patch('xtesting.core.unit.Suite.generate_stats')
    @mock.patch('unittest.TestLoader')
    @mock.patch('subunit.run.SubunitTestRunner.run')
    def _test_run(self, mock_result, status, result, *args):
        args[0].return_value = mock_result
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as m_open:
            self.assertEqual(self.psrunner.run(), status)
        m_open.assert_called_once_with(
            '{}/subunit_stream'.format(self.psrunner.res_dir), 'w')
        self.assertEqual(self.psrunner.is_successful(), result)
        args[0].assert_called_once_with(self.psrunner.suite)
        args[1].assert_not_called()
        args[2].assert_called_once_with(mock.ANY)
        args[3].assert_called_once_with(mock.ANY)
        args[4].assert_called_once_with(
            '{}/subunit_stream'.format(self.psrunner.res_dir))

    @mock.patch('xtesting.core.unit.Suite.generate_html')
    @mock.patch('xtesting.core.unit.Suite.generate_xunit')
    @mock.patch('xtesting.core.unit.Suite.generate_stats')
    @mock.patch('unittest.TestLoader')
    @mock.patch('subunit.run.SubunitTestRunner.run')
    def _test_run_name(self, name, mock_result, status, result, *args):
        args[0].return_value = mock_result
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as m_open:
            self.assertEqual(self.psrunner.run(name=name), status)
        m_open.assert_called_once_with(
            '{}/subunit_stream'.format(self.psrunner.res_dir), 'w')
        self.assertEqual(self.psrunner.is_successful(), result)
        args[0].assert_called_once_with(self.psrunner.suite)
        args[1].assert_called_once_with()
        args[2].assert_called_once_with(mock.ANY)
        args[3].assert_called_once_with(mock.ANY)
        args[4].assert_called_once_with(
            '{}/subunit_stream'.format(self.psrunner.res_dir))

    @mock.patch('xtesting.core.unit.Suite.generate_html')
    @mock.patch('xtesting.core.unit.Suite.generate_xunit')
    @mock.patch('xtesting.core.unit.Suite.generate_stats')
    @mock.patch('unittest.TestLoader')
    @mock.patch('subunit.run.SubunitTestRunner.run')
    @mock.patch('os.path.isdir', return_value=True)
    def _test_run_exc(self, exc, *args):
        args[1].return_value = mock.Mock(
            decorated=mock.Mock(
                testsRun=50, errors=[], failures=[]))
        args[3].side_effect = exc
        with mock.patch('six.moves.builtins.open',
                        mock.mock_open()) as m_open:
            self.assertEqual(
                self.psrunner.run(), testcase.TestCase.EX_RUN_ERROR)
        m_open.assert_not_called()
        self.assertEqual(
            self.psrunner.is_successful(),
            testcase.TestCase.EX_TESTCASE_FAILED)
        args[0].assert_called_once_with(self.psrunner.res_dir)
        args[1].assert_called_once_with(self.psrunner.suite)
        args[2].assert_not_called()
        args[3].assert_called_once_with(mock.ANY)
        args[4].assert_not_called()
        args[5].assert_not_called()

    def test_check_suite_null(self):
        self.assertEqual(unit.Suite().suite, None)
        self.psrunner.suite = None
        self.assertEqual(self.psrunner.run(), testcase.TestCase.EX_RUN_ERROR)

    @mock.patch('os.path.isdir', return_value=True)
    def test_run_no_ut(self, *args):
        mock_result = mock.Mock(
            decorated=mock.Mock(testsRun=0, errors=[], failures=[]))
        self._test_run(
            mock_result, testcase.TestCase.EX_RUN_ERROR,
            testcase.TestCase.EX_TESTCASE_FAILED)
        self.assertEqual(self.psrunner.result, 0)
        self.assertEqual(
            self.psrunner.details,
            {'errors': 0, 'failures': 0, 'testsRun': 0})
        args[0].assert_called_once_with(self.psrunner.res_dir)

    @mock.patch('os.path.isdir', return_value=True)
    def test_run_result_ko(self, *args):
        self.psrunner.criteria = 100
        mock_result = mock.Mock(
            decorated=mock.Mock(
                testsRun=50, errors=[('test1', 'error_msg1')],
                failures=[('test2', 'failure_msg1')]))
        self._test_run(
            mock_result, testcase.TestCase.EX_OK,
            testcase.TestCase.EX_TESTCASE_FAILED)
        self.assertEqual(self.psrunner.result, 96)
        self.assertEqual(
            self.psrunner.details,
            {'errors': 1, 'failures': 1, 'testsRun': 50})
        args[0].assert_called_once_with(self.psrunner.res_dir)

    @mock.patch('os.path.isdir', return_value=True)
    def test_run_result_ok_1(self, *args):
        mock_result = mock.Mock(
            decorated=mock.Mock(
                testsRun=50, errors=[], failures=[]))
        self._test_run(
            mock_result, testcase.TestCase.EX_OK,
            testcase.TestCase.EX_OK)
        self.assertEqual(self.psrunner.result, 100)
        self.assertEqual(
            self.psrunner.details,
            {'errors': 0, 'failures': 0, 'testsRun': 50})
        args[0].assert_called_once_with(self.psrunner.res_dir)

    @mock.patch('os.makedirs')
    @mock.patch('os.path.isdir', return_value=False)
    def test_run_result_ok_2(self, *args):
        mock_result = mock.Mock(
            decorated=mock.Mock(
                testsRun=50, errors=[], failures=[]))
        self._test_run(
            mock_result, testcase.TestCase.EX_OK,
            testcase.TestCase.EX_OK)
        self.assertEqual(self.psrunner.result, 100)
        self.assertEqual(
            self.psrunner.details,
            {'errors': 0, 'failures': 0, 'testsRun': 50})
        args[0].assert_called_once_with(self.psrunner.res_dir)
        args[1].assert_called_once_with(self.psrunner.res_dir)

    @mock.patch('unittest.TestLoader')
    def test_run_name_exc(self, mock_class=None):
        mock_obj = mock.Mock(side_effect=ImportError)
        mock_class.side_effect = mock_obj
        self.assertEqual(self.psrunner.run(name='foo'),
                         testcase.TestCase.EX_RUN_ERROR)
        mock_class.assert_called_once_with()
        mock_obj.assert_called_once_with()

    @mock.patch('os.path.isdir', return_value=True)
    def test_run_name(self, *args):
        mock_result = mock.Mock(
            decorated=mock.Mock(
                testsRun=50, errors=[], failures=[]))
        self._test_run_name(
            "foo", mock_result, testcase.TestCase.EX_OK,
            testcase.TestCase.EX_OK)
        self.assertEqual(self.psrunner.result, 100)
        self.assertEqual(
            self.psrunner.details,
            {'errors': 0, 'failures': 0, 'testsRun': 50})
        args[0].assert_called_once_with(self.psrunner.res_dir)

    def test_run_exc1(self):
        self._test_run_exc(AssertionError)

    def test_run_exc2(self):
        self._test_run_exc(ZeroDivisionError)

    def test_run_exc3(self):
        self._test_run_exc(Exception)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
