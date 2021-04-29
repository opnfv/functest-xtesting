#!/usr/bin/env python

# Copyright (c) 2021 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import logging
import unittest

import mock
import munch

from xtesting.core import ansible


class RunTesting(unittest.TestCase):

    def setUp(self):
        self.test = ansible.Ansible()

    @mock.patch("shutil.which", return_value=None)
    def test_check1(self, which):
        self.test.check_requirements()
        self.assertEqual(self.test.is_skipped, True)
        which.assert_called_once_with("ansible-playbook")

    @mock.patch("shutil.which", return_value='/usr/bin/ansible-playbook')
    def test_check2(self, which):
        self.test.check_requirements()
        self.assertEqual(self.test.is_skipped, False)
        which.assert_called_once_with("ansible-playbook")

    @mock.patch("os.path.isdir", return_value=False)
    def test_fail1(self, isdir):
        self.assertEqual(self.test.run(), self.test.EX_RUN_ERROR)
        isdir.assert_not_called()

    @mock.patch("os.path.isdir", return_value=False)
    def test_fail2(self, isdir):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(private_data_dir=private_data_dir),
            self.test.EX_RUN_ERROR)
        isdir.assert_called_once_with(private_data_dir)

    @mock.patch("ansible_runner.run", side_effect=Exception)
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("os.path.isdir", return_value=True)
    def test_fail3(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(private_data_dir=private_data_dir),
            self.test.EX_RUN_ERROR)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_not_called()
        args[3].assert_called_with(
            private_data_dir=private_data_dir, quiet=True,
            artifact_dir=self.test.res_dir)

    @mock.patch("ansible_runner.run", side_effect=Exception)
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.path.isdir", return_value=True)
    def test_fail4(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(private_data_dir=private_data_dir),
            self.test.EX_RUN_ERROR)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_called_once_with(self.test.res_dir)
        args[3].assert_called_with(
            private_data_dir=private_data_dir, quiet=True,
            artifact_dir=self.test.res_dir)

    @mock.patch("ansible_runner.run")
    @mock.patch("os.makedirs", side_effect=Exception)
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.path.isdir", return_value=True)
    def test_fail5(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(private_data_dir=private_data_dir),
            self.test.EX_RUN_ERROR)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_called_once_with(self.test.res_dir)
        args[3].assert_not_called()

    @mock.patch("ansible_runner.run", return_value={})
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.path.isdir", return_value=True)
    def test_fail6(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(
                private_data_dir=private_data_dir, quiet=False,
                artifact_dir="overridden"),
            self.test.EX_RUN_ERROR)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_called_once_with(self.test.res_dir)
        args[3].assert_called_with(
            private_data_dir=private_data_dir, quiet=False,
            artifact_dir=self.test.res_dir)

    @mock.patch("ansible_runner.run",
                return_value=munch.Munch(rc=0, stats={"foo": "bar"}))
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.path.isdir", return_value=True)
    def test_res_ok1(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(
                private_data_dir=private_data_dir, quiet=False,
                artifact_dir="overridden"),
            self.test.EX_OK)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_called_once_with(self.test.res_dir)
        args[3].assert_called_with(
            private_data_dir=private_data_dir, quiet=False,
            artifact_dir=self.test.res_dir)
        self.assertEqual(self.test.is_successful(), self.test.EX_OK)
        self.assertEqual(self.test.details, {"foo": "bar"})

    @mock.patch("ansible_runner.run",
                return_value=munch.Munch(rc=0, stats={"foo": "bar"}))
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.path.isdir", return_value=True)
    def test_res_ok2(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(
                private_data_dir=private_data_dir, quiet=True,
                artifact_dir="overridden"),
            self.test.EX_OK)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_called_once_with(self.test.res_dir)
        args[3].assert_called_with(
            private_data_dir=private_data_dir, quiet=True,
            artifact_dir=self.test.res_dir)
        self.assertEqual(self.test.is_successful(), self.test.EX_OK)
        self.assertEqual(self.test.details, {"foo": "bar"})

    @mock.patch("ansible_runner.run",
                return_value=munch.Munch(rc=0, stats={"foo": "bar"}))
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.path.isdir", return_value=True)
    def test_res_ok3(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(
                private_data_dir=private_data_dir, artifact_dir="overridden"),
            self.test.EX_OK)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_called_once_with(self.test.res_dir)
        args[3].assert_called_with(
            private_data_dir=private_data_dir, quiet=True,
            artifact_dir=self.test.res_dir)
        self.assertEqual(self.test.is_successful(), self.test.EX_OK)
        self.assertEqual(self.test.details, {"foo": "bar"})

    @mock.patch("ansible_runner.run",
                return_value=munch.Munch(rc=1, stats={"foo": "bar"}))
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists", return_value=False)
    @mock.patch("os.path.isdir", return_value=True)
    def test_res_ko(self, *args):
        private_data_dir = "titi"
        self.assertEqual(
            self.test.run(
                private_data_dir=private_data_dir, artifact_dir="overridden"),
            self.test.EX_OK)
        args[0].assert_called_once_with(private_data_dir)
        args[1].assert_called_once_with(self.test.res_dir)
        args[2].assert_called_once_with(self.test.res_dir)
        args[3].assert_called_with(
            private_data_dir=private_data_dir, quiet=True,
            artifact_dir=self.test.res_dir)
        self.assertEqual(self.test.is_successful(),
                         self.test.EX_TESTCASE_FAILED)
        self.assertEqual(self.test.details, {"foo": "bar"})


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
