#! /usr/bin/env python3

import logging
import time

import pytest
import xtesting


class Pytest(xtesting.core.testcase.TestCase):
    """pytest runner."""

    __logger = logging.getLogger(__name__)

    def run(self, **kwargs):
        try:
            dir = kwargs.pop('dir')
            options = kwargs.pop('options', [])
        except KeyError as err:
            self.__logger.exception(f"Missing args: {err.args[0]!r}")
            return self.EX_RUN_ERROR
        if kwargs:
            self.__logger.exception(f"Unexpected args {kwargs}")
            return self.EX_RUN_ERROR

        self.start_time = time.time()

        pytest.main(args=['--tb=no', '-p', 'xtesting.utils.pytesthooks'] + options + [dir])

        self.stop_time = time.time()
        self.details = xtesting.utils.pytesthooks.details
        self.result = 100
        return self.EX_OK
