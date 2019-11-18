#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

"""Define the class required to fully cover testcase."""

from datetime import datetime
import json
import logging
import os
import unittest

import botocore
import mock
import requests

from xtesting.core import testcase

__author__ = "Cedric Ollivier <cedric.ollivier@orange.com>"


class FakeTestCase(testcase.TestCase):
    # pylint: disable=too-many-instance-attributes

    def run(self, **kwargs):
        return testcase.TestCase.EX_OK


class AbstractTestCaseTesting(unittest.TestCase):

    def test_run_unimplemented(self):
        # pylint: disable=abstract-class-instantiated
        with self.assertRaises(TypeError):
            testcase.TestCase(case_name="base", project_name="xtesting")


class TestCaseTesting(unittest.TestCase):
    # pylint: disable=too-many-instance-attributes,too-many-public-methods

    _case_name = "base"
    _project_name = "xtesting"
    _published_result = "PASS"
    _test_db_url = "http://testresults.opnfv.org/test/api/v1/results"
    _headers = {'Content-Type': 'application/json'}

    def setUp(self):
        self.test = FakeTestCase(
            case_name=self._case_name, project_name=self._project_name)
        self.test.start_time = 1
        self.test.stop_time = 2
        self.test.result = 100
        self.test.details = {"Hello": "World"}
        os.environ['TEST_DB_URL'] = TestCaseTesting._test_db_url
        os.environ['TEST_DB_EXT_URL'] = TestCaseTesting._test_db_url
        os.environ['INSTALLER_TYPE'] = "installer_type"
        os.environ['DEPLOY_SCENARIO'] = "scenario"
        os.environ['NODE_NAME'] = "node_name"
        os.environ['BUILD_TAG'] = "foo-daily-master-bar"
        os.environ['S3_ENDPOINT_URL'] = "http://127.0.0.1:9000"
        os.environ['S3_DST_URL'] = "s3://xtesting/prefix"
        os.environ['HTTP_DST_URL'] = "http://127.0.0.1/prefix"

    def test_run_fake(self):
        self.assertEqual(self.test.run(), testcase.TestCase.EX_OK)

    def _test_pushdb_missing_attribute(self):
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_PUSH_TO_DB_ERROR)

    def test_pushdb_no_project_name(self):
        self.test.project_name = None
        self._test_pushdb_missing_attribute()

    def test_pushdb_no_case_name(self):
        self.test.case_name = None
        self._test_pushdb_missing_attribute()

    def test_pushdb_no_start_time(self):
        self.test.start_time = None
        self._test_pushdb_missing_attribute()

    def test_pushdb_no_stop_time(self):
        self.test.stop_time = None
        self._test_pushdb_missing_attribute()

    def _test_pushdb_missing_env(self, var):
        del os.environ[var]
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_PUSH_TO_DB_ERROR)

    def test_pushdb_no_db_url(self):
        self._test_pushdb_missing_env('TEST_DB_URL')

    def test_pushdb_no_installer_type(self):
        self._test_pushdb_missing_env('INSTALLER_TYPE')

    def test_pushdb_no_deploy_scenario(self):
        self._test_pushdb_missing_env('DEPLOY_SCENARIO')

    def test_pushdb_no_node_name(self):
        self._test_pushdb_missing_env('NODE_NAME')

    def test_pushdb_no_build_tag(self):
        self._test_pushdb_missing_env('BUILD_TAG')

    @mock.patch('requests.post')
    def test_pushdb_bad_start_time(self, mock_function=None):
        self.test.start_time = "1"
        self.assertEqual(
            self.test.push_to_db(),
            testcase.TestCase.EX_PUSH_TO_DB_ERROR)
        mock_function.assert_not_called()

    @mock.patch('requests.post')
    def test_pushdb_bad_end_time(self, mock_function=None):
        self.test.stop_time = "2"
        self.assertEqual(
            self.test.push_to_db(),
            testcase.TestCase.EX_PUSH_TO_DB_ERROR)
        mock_function.assert_not_called()

    @mock.patch('requests.post')
    def test_pushdb_skipped_test(self, mock_function=None):
        self.test.is_skipped = True
        self.assertEqual(
            self.test.push_to_db(),
            testcase.TestCase.EX_PUSH_TO_DB_ERROR)
        mock_function.assert_not_called()

    def _get_data(self):
        return {
            "build_tag": os.environ['BUILD_TAG'],
            "case_name": self._case_name,
            "criteria": 'PASS' if self.test.is_successful(
                ) == self.test.EX_OK else 'FAIL',
            "details": self.test.details,
            "installer": os.environ['INSTALLER_TYPE'],
            "pod_name": os.environ['NODE_NAME'],
            "project_name": self.test.project_name,
            "scenario": os.environ['DEPLOY_SCENARIO'],
            "start_date": datetime.fromtimestamp(
                self.test.start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "stop_date": datetime.fromtimestamp(
                self.test.stop_time).strftime('%Y-%m-%d %H:%M:%S'),
            "version": "master"}

    @mock.patch('requests.post')
    def _test_pushdb_version(self, mock_function=None, **kwargs):
        payload = self._get_data()
        payload["version"] = kwargs.get("version", "unknown")
        self.assertEqual(self.test.push_to_db(), testcase.TestCase.EX_OK)
        mock_function.assert_called_once_with(
            os.environ['TEST_DB_URL'],
            data=json.dumps(payload, sort_keys=True),
            headers=self._headers)

    def test_pushdb_daily_job(self):
        self._test_pushdb_version(version="master")

    def test_pushdb_weekly_job(self):
        os.environ['BUILD_TAG'] = 'foo-weekly-master-bar'
        self._test_pushdb_version(version="master")

    def test_pushdb_random_build_tag(self):
        os.environ['BUILD_TAG'] = 'whatever'
        self._test_pushdb_version(version="unknown")

    @mock.patch('requests.post', return_value=mock.Mock(
        raise_for_status=mock.Mock(
            side_effect=requests.exceptions.HTTPError)))
    def test_pushdb_http_errors(self, mock_function=None):
        self.assertEqual(
            self.test.push_to_db(),
            testcase.TestCase.EX_PUSH_TO_DB_ERROR)
        mock_function.assert_called_once_with(
            os.environ['TEST_DB_URL'],
            data=json.dumps(self._get_data(), sort_keys=True),
            headers=self._headers)

    def test_check_requirements(self):
        self.test.check_requirements()
        self.assertEqual(self.test.is_skipped, False)

    def test_check_criteria_missing(self):
        self.test.criteria = None
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_missing(self):
        self.test.result = None
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_failed(self):
        # Backward compatibility
        # It must be removed as soon as TestCase subclasses
        # stop setting result = 'PASS' or 'FAIL'.
        self.test.result = 'FAIL'
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_pass(self):
        # Backward compatibility
        # It must be removed as soon as TestCase subclasses
        # stop setting result = 'PASS' or 'FAIL'.
        self.test.result = 'PASS'
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_OK)

    def test_check_result_skip(self):
        self.test.is_skipped = True
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_SKIPPED)

    def test_check_result_lt(self):
        self.test.result = 50
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_eq(self):
        self.test.result = 100
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_OK)

    def test_check_result_gt(self):
        self.test.criteria = 50
        self.test.result = 100
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_OK)

    def test_check_result_zero(self):
        self.test.criteria = 0
        self.test.result = 0
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_get_duration_start_ko(self):
        self.test.start_time = None
        self.assertEqual(self.test.get_duration(), "XX:XX")
        self.test.start_time = 0
        self.assertEqual(self.test.get_duration(), "XX:XX")

    def test_get_duration_end_ko(self):
        self.test.stop_time = None
        self.assertEqual(self.test.get_duration(), "XX:XX")
        self.test.stop_time = 0
        self.assertEqual(self.test.get_duration(), "XX:XX")

    def test_get_invalid_duration(self):
        self.test.start_time = 2
        self.test.stop_time = 1
        self.assertEqual(self.test.get_duration(), "XX:XX")

    def test_get_zero_duration(self):
        self.test.start_time = 2
        self.test.stop_time = 2
        self.assertEqual(self.test.get_duration(), "00:00")

    def test_get_duration(self):
        self.test.start_time = 1
        self.test.stop_time = 180
        self.assertEqual(self.test.get_duration(), "02:59")

    def test_get_duration_skipped_test(self):
        self.test.is_skipped = True
        self.assertEqual(self.test.get_duration(), "00:00")

    def test_str_project_name_ko(self):
        self.test.project_name = None
        self.assertIn("FakeTestCase object at", str(self.test))

    def test_str_case_name_ko(self):
        self.test.case_name = None
        self.assertIn("FakeTestCase object at", str(self.test))

    def test_str_pass(self):
        duration = '01:01'
        with mock.patch.object(self.test, 'get_duration',
                               return_value=duration), \
                mock.patch.object(self.test, 'is_successful',
                                  return_value=testcase.TestCase.EX_OK):
            message = str(self.test)
        self.assertIn(self._project_name, message)
        self.assertIn(self._case_name, message)
        self.assertIn(duration, message)
        self.assertIn('PASS', message)

    def test_str_fail(self):
        duration = '00:59'
        with mock.patch.object(self.test, 'get_duration',
                               return_value=duration), \
                mock.patch.object(
                    self.test, 'is_successful',
                    return_value=testcase.TestCase.EX_TESTCASE_FAILED):
            message = str(self.test)
        self.assertIn(self._project_name, message)
        self.assertIn(self._case_name, message)
        self.assertIn(duration, message)
        self.assertIn('FAIL', message)

    def test_str_skip(self):
        self.test.is_skipped = True
        message = str(self.test)
        self.assertIn(self._project_name, message)
        self.assertIn(self._case_name, message)
        self.assertIn("00:00", message)
        self.assertIn('SKIP', message)

    def test_clean(self):
        self.assertEqual(self.test.clean(), None)

    def _test_publish_artifacts_nokw(self, key):
        del os.environ[key]
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_PUBLISH_ARTIFACTS_ERROR)

    def test_publish_artifacts_exc1(self):
        for key in ["S3_ENDPOINT_URL", "S3_DST_URL", "HTTP_DST_URL"]:
            self._test_publish_artifacts_nokw(key)

    @mock.patch('boto3.resource',
                side_effect=botocore.exceptions.NoCredentialsError)
    def test_publish_artifacts_exc2(self, *args):
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_PUBLISH_ARTIFACTS_ERROR)
        args[0].assert_called_once_with(
            's3', endpoint_url=os.environ['S3_ENDPOINT_URL'])

    @mock.patch('boto3.resource', side_effect=Exception)
    def test_publish_artifacts_exc3(self, *args):
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_PUBLISH_ARTIFACTS_ERROR)
        args[0].assert_called_once_with(
            's3', endpoint_url=os.environ['S3_ENDPOINT_URL'])

    @mock.patch('boto3.resource')
    def test_publish_artifacts_exc4(self, *args):
        args[0].return_value.meta.client.head_bucket.side_effect = Exception
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_PUBLISH_ARTIFACTS_ERROR)
        args[0].assert_called_once_with(
            's3', endpoint_url=os.environ['S3_ENDPOINT_URL'])

    @mock.patch('boto3.resource')
    def test_publish_artifacts_exc5(self, *args):
        error_response = {'Error': {'Code': '403'}}
        mock_head_bucket = args[0].return_value.meta.client.head_bucket
        mock_head_bucket.side_effect = botocore.exceptions.ClientError(
            error_response, 'Foo')
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_PUBLISH_ARTIFACTS_ERROR)
        args[0].assert_called_once_with(
            's3', endpoint_url=os.environ['S3_ENDPOINT_URL'])

    @mock.patch('mimetypes.guess_type', return_value=(None, None))
    @mock.patch('boto3.resource')
    @mock.patch('os.walk', return_value=[])
    def test_publish_artifacts1(self, *args):
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_OK)
        args[0].assert_called_once_with(self.test.res_dir)
        args[1].assert_called_once_with(
            's3', endpoint_url=os.environ['S3_ENDPOINT_URL'])

    @mock.patch('mimetypes.guess_type', return_value=(None, None))
    @mock.patch('boto3.resource')
    @mock.patch('os.walk', return_value=[])
    def test_publish_artifacts2(self, *args):
        error_response = {'Error': {'Code': '404'}}
        mock_head_bucket = args[1].return_value.meta.client.head_bucket
        mock_head_bucket.side_effect = botocore.exceptions.ClientError(
            error_response, 'NoSuchBucket')
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_OK)
        args[0].assert_called_once_with(self.test.res_dir)
        args[1].assert_called_once_with(
            's3', endpoint_url=os.environ['S3_ENDPOINT_URL'])

    @mock.patch('mimetypes.guess_type', return_value=(None, None))
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('boto3.resource')
    @mock.patch('os.walk',
                return_value=[
                    (testcase.TestCase.dir_results, ('',), ('bar',))])
    def test_publish_artifacts3(self, *args):
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_OK)
        args[0].assert_called_once_with(self.test.res_dir)
        expected = [
            mock.call('s3', endpoint_url=os.environ['S3_ENDPOINT_URL']),
            mock.call().meta.client.head_bucket(Bucket='xtesting'),
            mock.call().Bucket('xtesting'),
            mock.call().Bucket().upload_file(
                '/var/lib/xtesting/results/xtesting.log',
                'prefix/xtesting.log',
                Config=mock.ANY,
                ExtraArgs={'ContentType': 'application/octet-stream'}),
            mock.call().Bucket('xtesting'),
            mock.call().Bucket().upload_file(
                '/var/lib/xtesting/results/xtesting.debug.log',
                'prefix/xtesting.debug.log',
                Config=mock.ANY,
                ExtraArgs={'ContentType': 'application/octet-stream'}),
            mock.call().Bucket('xtesting'),
            mock.call().Bucket().upload_file(
                '/var/lib/xtesting/results/bar', 'prefix/bar',
                Config=mock.ANY,
                ExtraArgs={'ContentType': 'application/octet-stream'})]
        self.assertEqual(args[1].mock_calls, expected)

    @mock.patch('mimetypes.guess_type', return_value=('text/plain', None))
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('boto3.resource')
    @mock.patch('os.walk',
                return_value=[
                    (testcase.TestCase.dir_results, ('',), ('bar',))])
    def test_publish_artifacts4(self, *args):
        self.assertEqual(self.test.publish_artifacts(),
                         testcase.TestCase.EX_OK)
        args[0].assert_called_once_with(self.test.res_dir)
        expected = [
            mock.call('s3', endpoint_url=os.environ['S3_ENDPOINT_URL']),
            mock.call().meta.client.head_bucket(Bucket='xtesting'),
            mock.call().Bucket('xtesting'),
            mock.call().Bucket().upload_file(
                '/var/lib/xtesting/results/xtesting.log',
                'prefix/xtesting.log',
                Config=mock.ANY,
                ExtraArgs={'ContentType': 'text/plain'}),
            mock.call().Bucket('xtesting'),
            mock.call().Bucket().upload_file(
                '/var/lib/xtesting/results/xtesting.debug.log',
                'prefix/xtesting.debug.log',
                Config=mock.ANY,
                ExtraArgs={'ContentType': 'text/plain'}),
            mock.call().Bucket('xtesting'),
            mock.call().Bucket().upload_file(
                '/var/lib/xtesting/results/bar', 'prefix/bar',
                Config=mock.ANY,
                ExtraArgs={'ContentType': 'text/plain'})]
        self.assertEqual(args[1].mock_calls, expected)

if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
