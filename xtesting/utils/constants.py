#!/usr/bin/env python

# pylint: disable=missing-docstring

import os

ENV_FILE = '/var/lib/xtesting/conf/env_file'

RESULTS_DIR = '/var/lib/xtesting/results'
LOG_PATH = os.path.join(RESULTS_DIR, 'xtesting.log')
DEBUG_LOG_PATH = os.path.join(RESULTS_DIR, 'xtesting.debug.log')

INI_PATH = 'ci/logging.ini'
DEBUG_INI_PATH = 'ci/logging.debug.ini'
