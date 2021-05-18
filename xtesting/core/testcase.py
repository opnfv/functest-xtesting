#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define the parent class of all Xtesting TestCases."""

import abc
from datetime import datetime
import json
import logging
import mimetypes
import os
import re
import sys

import boto3
from boto3.s3.transfer import TransferConfig
import botocore
import prettytable
import requests
import six
from six.moves import urllib

from xtesting.utils import decorators
from xtesting.utils import env
from xtesting.utils import constants

__author__ = "Cedric Ollivier <cedric.ollivier@orange.com>"


@six.add_metaclass(abc.ABCMeta)
class TestCase():
    # pylint: disable=too-many-instance-attributes
    """Base model for single test case."""

    EX_OK = os.EX_OK
    """everything is OK"""

    EX_RUN_ERROR = os.EX_SOFTWARE
    """run() failed"""

    EX_PUSH_TO_DB_ERROR = os.EX_SOFTWARE - 1
    """push_to_db() failed"""

    EX_TESTCASE_FAILED = os.EX_SOFTWARE - 2
    """results are false"""

    EX_TESTCASE_SKIPPED = os.EX_SOFTWARE - 3
    """requirements are unmet"""

    EX_PUBLISH_ARTIFACTS_ERROR = os.EX_SOFTWARE - 4
    """publish_artifacts() failed"""

    dir_results = constants.RESULTS_DIR
    _job_name_rule = "(dai|week)ly-(.+?)-[0-9]*"
    headers = {'Content-Type': 'application/json'}
    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        self.details = {}
        self.project_name = kwargs.get('project_name', 'xtesting')
        self.case_name = kwargs.get('case_name', '')
        self.criteria = kwargs.get('criteria', 100)
        self.result = 0
        self.start_time = 0
        self.stop_time = 0
        self.is_skipped = False
        self.output_log_name = os.path.basename(constants.LOG_PATH)
        self.output_debug_log_name = os.path.basename(constants.DEBUG_LOG_PATH)
        self.res_dir = os.path.join(self.dir_results, self.case_name)

    def __str__(self):
        try:
            assert self.project_name
            assert self.case_name
            if self.is_skipped:
                result = 'SKIP'
            else:
                result = 'PASS' if(self.is_successful(
                    ) == TestCase.EX_OK) else 'FAIL'
            msg = prettytable.PrettyTable(
                header_style='upper', padding_width=5,
                field_names=['test case', 'project', 'duration',
                             'result'])
            msg.add_row([self.case_name, self.project_name,
                         self.get_duration(), result])
            return msg.get_string()
        except AssertionError:
            self.__logger.error("We cannot print invalid objects")
            return super(TestCase, self).__str__()

    def get_duration(self):
        """Return the duration of the test case.

        Returns:
            duration if start_time and stop_time are set
            "XX:XX" otherwise.
        """
        try:
            if self.is_skipped:
                return "00:00"
            assert self.start_time
            assert self.stop_time
            if self.stop_time < self.start_time:
                return "XX:XX"
            return "{}:{}".format(
                str(int(self.stop_time - self.start_time) // 60).zfill(2),
                str(int(self.stop_time - self.start_time) % 60).zfill(2))
        except Exception:  # pylint: disable=broad-except
            self.__logger.error("Please run test before getting the duration")
            return "XX:XX"

    def is_successful(self):
        """Interpret the result of the test case.

        It allows getting the result of TestCase. It completes run()
        which only returns the execution status.

        It can be overriden if checking result is not suitable.

        Returns:
            TestCase.EX_OK if result is 'PASS'.
            TestCase.EX_TESTCASE_SKIPPED if test case is skipped.
            TestCase.EX_TESTCASE_FAILED otherwise.
        """
        try:
            if self.is_skipped:
                return TestCase.EX_TESTCASE_SKIPPED
            assert self.criteria
            assert self.result is not None
            if (not isinstance(self.result, str) and
                    not isinstance(self.criteria, str)):
                if self.result >= self.criteria:
                    return TestCase.EX_OK
            else:
                # Backward compatibility
                # It must be removed as soon as TestCase subclasses
                # stop setting result = 'PASS' or 'FAIL'.
                # In this case criteria is unread.
                self.__logger.warning(
                    "Please update result which must be an int!")
                if self.result == 'PASS':
                    return TestCase.EX_OK
        except AssertionError:
            self.__logger.error("Please run test before checking the results")
        return TestCase.EX_TESTCASE_FAILED

    def check_requirements(self):  # pylint: disable=no-self-use
        """Check the requirements of the test case.

        It can be overriden on purpose.
        """
        self.is_skipped = False

    @abc.abstractmethod
    def run(self, **kwargs):
        """Run the test case.

        It allows running TestCase and getting its execution
        status.

        The subclasses must override the default implementation which
        is false on purpose.

        The new implementation must set the following attributes to
        push the results to DB:

            * result,
            * start_time,
            * stop_time.

        Args:
            kwargs: Arbitrary keyword arguments.
        """

    @decorators.can_dump_request_to_file
    def push_to_db(self):
        """Push the results of the test case to the DB.

        It allows publishing the results and checking the status.

        It could be overriden if the common implementation is not
        suitable.

        The following attributes must be set before pushing the results to DB:

            * project_name,
            * case_name,
            * result,
            * start_time,
            * stop_time.

        The next vars must be set in env:

            * TEST_DB_URL,
            * INSTALLER_TYPE,
            * DEPLOY_SCENARIO,
            * NODE_NAME,
            * BUILD_TAG.

        Returns:
            TestCase.EX_OK if results were pushed to DB.
            TestCase.EX_PUSH_TO_DB_ERROR otherwise.
        """
        try:
            if self.is_skipped:
                return TestCase.EX_PUSH_TO_DB_ERROR
            assert self.project_name
            assert self.case_name
            assert self.start_time
            assert self.stop_time
            url = env.get('TEST_DB_URL')
            data = {"project_name": self.project_name,
                    "case_name": self.case_name,
                    "details": self.details}
            data["installer"] = env.get('INSTALLER_TYPE')
            data["scenario"] = env.get('DEPLOY_SCENARIO')
            data["pod_name"] = env.get('NODE_NAME')
            data["build_tag"] = env.get('BUILD_TAG')
            data["criteria"] = 'PASS' if self.is_successful(
                ) == TestCase.EX_OK else 'FAIL'
            data["start_date"] = datetime.fromtimestamp(
                self.start_time).strftime('%Y-%m-%d %H:%M:%S')
            data["stop_date"] = datetime.fromtimestamp(
                self.stop_time).strftime('%Y-%m-%d %H:%M:%S')
            try:
                data["version"] = re.search(
                    TestCase._job_name_rule,
                    env.get('BUILD_TAG')).group(2)
            except Exception:  # pylint: disable=broad-except
                data["version"] = "unknown"
            req = requests.post(
                url, data=json.dumps(data, sort_keys=True),
                headers=self.headers)
            req.raise_for_status()
            if urllib.parse.urlparse(url).scheme != "file":
                # href must be postprocessed as OPNFV testapi is misconfigured
                # (localhost is returned)
                uid = re.sub(r'^.*/api/v1/results/*', '', req.json()["href"])
                netloc = env.get('TEST_DB_EXT_URL') if env.get(
                    'TEST_DB_EXT_URL') else env.get('TEST_DB_URL')
                self.__logger.info(
                    "The results were successfully pushed to DB: \n\n%s\n",
                    os.path.join(netloc, uid))
        except AssertionError:
            self.__logger.exception(
                "Please run test before publishing the results")
            return TestCase.EX_PUSH_TO_DB_ERROR
        except requests.exceptions.HTTPError:
            self.__logger.exception("The HTTP request raises issues")
            return TestCase.EX_PUSH_TO_DB_ERROR
        except Exception:  # pylint: disable=broad-except
            self.__logger.exception("The results cannot be pushed to DB")
            return TestCase.EX_PUSH_TO_DB_ERROR
        return TestCase.EX_OK

    def publish_artifacts(self):  # pylint: disable=too-many-locals
        """Push the artifacts to the S3 repository.

        It allows publishing the artifacts.

        It could be overriden if the common implementation is not
        suitable.

        The credentials must be configured before publishing the artifacts:

            * fill ~/.aws/credentials or ~/.boto,
            * set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in env.

        The next vars must be set in env:

            * S3_ENDPOINT_URL (http://127.0.0.1:9000),
            * S3_DST_URL (s3://xtesting/prefix),
            * HTTP_DST_URL (http://127.0.0.1/prefix).

        Returns:
            TestCase.EX_OK if artifacts were published to repository.
            TestCase.EX_PUBLISH_ARTIFACTS_ERROR otherwise.
        """
        try:
            b3resource = boto3.resource(
                's3', endpoint_url=os.environ["S3_ENDPOINT_URL"])
            dst_s3_url = os.environ["S3_DST_URL"]
            multipart_threshold = 5 * 1024 ** 5 if "google" in os.environ[
                "S3_ENDPOINT_URL"] else 8 * 1024 * 1024
            config = TransferConfig(multipart_threshold=multipart_threshold)
            bucket_name = urllib.parse.urlparse(dst_s3_url).netloc
            try:
                b3resource.meta.client.head_bucket(Bucket=bucket_name)
            except botocore.exceptions.ClientError as exc:
                error_code = exc.response['Error']['Code']
                if error_code == '404':
                    # pylint: disable=no-member
                    b3resource.create_bucket(Bucket=bucket_name)
                else:
                    typ, value, traceback = sys.exc_info()
                    six.reraise(typ, value, traceback)
            except Exception:  # pylint: disable=broad-except
                typ, value, traceback = sys.exc_info()
                six.reraise(typ, value, traceback)
            path = urllib.parse.urlparse(dst_s3_url).path.strip("/")
            dst_http_url = os.environ["HTTP_DST_URL"]
            output_str = "\n"
            self.details["links"] = []
            for log_file in [self.output_log_name, self.output_debug_log_name]:
                if os.path.exists(os.path.join(self.dir_results, log_file)):
                    abs_file = os.path.join(self.dir_results, log_file)
                    mime_type = mimetypes.guess_type(abs_file)
                    self.__logger.debug(
                        "Publishing %s %s", abs_file, mime_type)
                    # pylint: disable=no-member
                    b3resource.Bucket(bucket_name).upload_file(
                        abs_file, os.path.join(path, log_file), Config=config,
                        ExtraArgs={'ContentType': mime_type[
                            0] or 'application/octet-stream'})
                    link = os.path.join(dst_http_url, log_file)
                    output_str += "\n{}".format(link)
                    self.details["links"].append(link)
            for root, _, files in os.walk(self.res_dir):
                for pub_file in files:
                    abs_file = os.path.join(root, pub_file)
                    mime_type = mimetypes.guess_type(abs_file)
                    self.__logger.debug(
                        "Publishing %s %s", abs_file, mime_type)
                    # pylint: disable=no-member
                    b3resource.Bucket(bucket_name).upload_file(
                        abs_file,
                        os.path.join(path, os.path.relpath(
                            os.path.join(root, pub_file),
                            start=self.dir_results)),
                        Config=config,
                        ExtraArgs={'ContentType': mime_type[
                            0] or 'application/octet-stream'})
                    link = os.path.join(dst_http_url, os.path.relpath(
                        os.path.join(root, pub_file),
                        start=self.dir_results))
                    output_str += "\n{}".format(link)
                    self.details["links"].append(link)
            self.__logger.info(
                "All artifacts were successfully published: %s\n", output_str)
            return TestCase.EX_OK
        except KeyError as ex:
            self.__logger.error("Please check env var: %s", str(ex))
            return TestCase.EX_PUBLISH_ARTIFACTS_ERROR
        except botocore.exceptions.NoCredentialsError:
            self.__logger.error(
                "Please fill ~/.aws/credentials, ~/.boto or set "
                "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in env")
            return TestCase.EX_PUBLISH_ARTIFACTS_ERROR
        except Exception:  # pylint: disable=broad-except
            self.__logger.exception("Cannot publish the artifacts")
            return TestCase.EX_PUBLISH_ARTIFACTS_ERROR

    def clean(self):
        """Clean the resources.

        It can be overriden if resources must be deleted after
        running the test case.
        """
