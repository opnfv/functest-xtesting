#!/usr/bin/env python

# Copyright (c) 2019 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import os
import sys

import pkg_resources

ENV_FILE = '/var/lib/xtesting/conf/env_file'

XTESTING_PATHES = [
    "~/.xtesting", "/etc/xtesting", os.path.join(sys.prefix + "/etc/xtesting")]

TESTCASE_DESCRIPTION = 'testcases.yaml'
TESTCASE_DESCRIPTION_DEFAULT = pkg_resources.resource_filename(
    'xtesting', f'ci/{TESTCASE_DESCRIPTION}')

RESULTS_DIR = '/var/lib/xtesting/results'
LOG_PATH = os.path.join(RESULTS_DIR, 'xtesting.log')
DEBUG_LOG_PATH = os.path.join(RESULTS_DIR, 'xtesting.debug.log')

INI_PATH_DEFAULT = pkg_resources.resource_filename(
    'xtesting', 'ci/logging.ini')
DEBUG_INI_PATH_DEFAULT = pkg_resources.resource_filename(
    'xtesting', 'ci/logging.debug.ini')
