#!/usr/bin/env python

# Copyright (c) 2022 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import os

from xtesting.utils import constants


def get_xtesting_config(filename, default):
    """Search Xtesting configs (i.e. testcases.yaml)"""
    for path in constants.XTESTING_PATHES:
        abspath = os.path.abspath(os.path.expanduser(path))
        if os.path.isfile(os.path.join(abspath, filename)):
            return os.path.join(abspath, filename)
    return default
