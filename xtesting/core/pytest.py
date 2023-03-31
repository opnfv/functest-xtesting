#! /usr/bin/env python3

import logging
import time

import pytest

from xtesting.core import testcase
from xtesting.utils import pytesthooks


class Pytest(testcase.TestCase):

    """Pytest driver

    The pytest driver can be used on every test set written for pytest.
    Given a pytest package that is launched with the command:

    .. code-block:: shell

        pytest --opt1 arg1 --opt2 testdir

    it can be executed by xtesting with the following testcase.yaml:

    .. code-block:: yaml

        run:
          name: pytest
          args:
            opt1: arg1
            opt2: arg2
    """

    __logger = logging.getLogger(__name__)

    def run(self, **args):
        # parsing args
        #  - 'dir' is mandatory
        #  - 'options' is an optional list or a dict flatten to a list
        status = self.EX_RUN_ERROR
        self.start_time = time.time()
        try:
            pydir = args.pop('dir')
            options = args.pop('options', {})
            options['html'] = f'{self.res_dir}/results.html'
            options['junitxml'] = f'{self.res_dir}/results.xml'
            if 'tb' not in options:
                options['tb'] = 'no'
            options = [
                str(item) for opt in zip([f'--{k}' if len(str(k)) > 1 else
                f'-{k}' for k in options.keys()], options.values())
                for item in opt if item is not None]
            pytest.main(
                args=[pydir] + ['-p', 'xtesting.utils.pytesthooks'] + options)
            self.details = pytesthooks.details
            self.result = pytesthooks.result
            status = self.EX_OK
        except Exception:  # pylint: # pylint: disable=broad-except
            self.__logger.exception("Cannot execute pytest")
        self.stop_time = time.time()
        return status
