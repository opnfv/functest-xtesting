#!/usr/bin/env python

# Copyright (c) 2016 Ericsson AB and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""TierBuilder class to parse testcases config file"""

import re
import yaml

from xtesting.ci import tier_handler
from xtesting.utils import env


class TierBuilder():
    # pylint: disable=missing-docstring

    def __init__(self, testcases_file):
        self.ci_installer = env.get('INSTALLER_TYPE')
        self.ci_scenario = env.get('DEPLOY_SCENARIO')
        self.testcases_file = testcases_file
        self.dic_tier_array = None
        self.tier_objects = []
        self.testcases_yaml = None
        self.generate_tiers()

    def read_test_yaml(self):
        with open(self.testcases_file, encoding='utf-8') as tc_file:
            self.testcases_yaml = yaml.safe_load(tc_file)

        self.dic_tier_array = []
        for tier in self.testcases_yaml.get("tiers"):
            self.dic_tier_array.append(tier)

    def generate_tiers(self):
        if self.dic_tier_array is None:
            self.read_test_yaml()

        del self.tier_objects[:]
        for dic_tier in self.dic_tier_array:
            tier = tier_handler.Tier(
                name=dic_tier['name'],
                description=dic_tier.get('description', ''))
            for dic_testcase in dic_tier['testcases']:
                testcase = tier_handler.TestCase(
                    name=dic_testcase['case_name'],
                    enabled=dic_testcase.get('enabled', True),
                    skipped=False,
                    criteria=dic_testcase.get('criteria', 100),
                    blocking=dic_testcase.get('blocking', True),
                    description=dic_testcase.get('description', ''),
                    project=dic_testcase['project_name'])
                if not dic_testcase.get('dependencies'):
                    if testcase.is_enabled():
                        tier.add_test(testcase)
                    else:
                        testcase.skipped = True
                        tier.skip_test(testcase)
                else:
                    for dependency in dic_testcase['dependencies']:
                        kenv = list(dependency.keys())[0]
                        if not re.search(dependency[kenv],
                                         env.get(kenv) or ''):
                            testcase.skipped = True
                            tier.skip_test(testcase)
                            break
                    else:
                        if testcase.is_enabled():
                            tier.add_test(testcase)
                        else:
                            testcase.skipped = True
                            tier.skip_test(testcase)
            self.tier_objects.append(tier)

    def get_tiers(self):
        return self.tier_objects

    def get_tier_names(self):
        tier_names = []
        for tier in self.tier_objects:
            tier_names.append(tier.get_name())
        return tier_names

    def get_tier(self, tier_name):
        for i, _ in enumerate(self.tier_objects):
            if self.tier_objects[i].get_name() == tier_name:
                return self.tier_objects[i]
        return None

    def get_tier_name(self, test_name):
        for i, _ in enumerate(self.tier_objects):
            if self.tier_objects[i].is_test(test_name):
                return self.tier_objects[i].name
        return None

    def get_test(self, test_name):
        for i, _ in enumerate(self.tier_objects):
            if self.tier_objects[i].is_test(test_name):
                return self.tier_objects[i].get_test(test_name)
        return None

    def get_tests(self, tier_name):
        for i, _ in enumerate(self.tier_objects):
            if self.tier_objects[i].get_name() == tier_name:
                return self.tier_objects[i].get_tests()
        return None

    def __str__(self):
        output = ""
        for i, _ in enumerate(self.tier_objects):
            output += str(self.tier_objects[i]) + "\n"
        return output
