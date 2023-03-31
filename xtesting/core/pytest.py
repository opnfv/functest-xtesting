#! /usr/bin/env python3

import logging
import time

import pytest
import xtesting


class Pytest(xtesting.core.testcase.TestCase):
    """pytest driver

    The 'pytest driver' can be used on every test set written for pytest.
    Given a pytest package that is launched with the command:

    `pytest --opt1 arg1 --opt2 testdir`

    it can be executed by xtesting with the following testcase.yaml:

    ```yaml
     run:
        name: pytest
        args:
          dir: testdir
          options:
            opt1: arg1
            opt2: null
    ```

    options can be written as a list of strings `['--opt1', 'arg1', '--opt2']`
    """

    logger = logging.getLogger('pytest')

    def run(self, **args):
        # parsing args
        #  - 'dir' is mandatory
        #  - 'options' is an optional list or a dict flatten to a list
        try:
            dir = args.pop('dir')
            options = args.pop('options', [])
            if isinstance(options, dict):
                options = [str(item) for opt in
                           zip([f'--{k}' if len(str(k)) > 1 else f'-{k}' for k in options.keys()], options.values())
                           for item in opt if item is not None]
        except KeyError as err:
            self.logger.exception(f"Missing args: {err.args[0]!r}")
            return self.EX_RUN_ERROR
        if args:
            self.logger.exception(f"Unexpected args {args}")
            return self.EX_RUN_ERROR

        # running pytest with 'options' in 'dir'
        #  the pytesthooks initiates an empty 'details' and populates it with individual test results
        self.start_time = time.time()
        pytest.main(args=[dir] + ['--tb=no', '-p', 'xtesting.utils.pytesthooks'] + options)
        self.stop_time = time.time()

        # fectching results in pytesthooks
        self.details = xtesting.utils.pytesthooks.details
        self.result = xtesting.utils.pytesthooks.result
        return self.EX_OK
