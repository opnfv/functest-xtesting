import logging
import os
import time
import ansible_runner

from xtesting.core import testcase

class AnsibleFeature(testcase.TestCase):
    """Class designed to run ansible playbook."""

    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super(AnsibleFeature, self).__init__(**kwargs)
        self.result_file = "{}/{}.log".format(self.res_dir, self.case_name)

    def check_requirements(self):
        self.__logger.info("Checking prerequisite...")
        flag = False
        if os.path.exists("/src/inventory"):
            pass
        else:
            flag = True
            self.__logger.error("inventory file is not mounted...")

        if os.path.exists("/src/env/passwords"):
            pass
        else:
            flag = True
            self.__logger.error("password file is not mounted...")

        if flag:
            self.is_skipped = True
        else:
            self.is_skipped = False

    def run(self, **kwargs):
        """
        Execute the cmd passed as arg

        Args:
            kwargs: Arbitrary keyword arguments.

        Returns:
            0 if playbook executed successfully,
            non zero otherwise.
        """
        self.start_time = time.time()
        self.result = 0
        exit_code = testcase.TestCase.EX_RUN_ERROR
        try:
            cmd = kwargs["playbook_path"]
            console = kwargs["console"] if "console" in kwargs else False
            if not os.path.isdir(self.res_dir):
                os.makedirs(self.res_dir)
            with open(self.result_file, 'w') as f_stdout:
                self.__logger.info("Calling %s", cmd)
                r = ansible_runner.run(private_data_dir="/src/", playbook=cmd, cmdline="-k")
                self.__logger.info("Return status: %s", r.rc)
            with open(self.result_file, 'r') as f_stdin:
                self.__logger.debug("$ %s\n%s", cmd, f_stdin.read().rstrip())

            if r.rc == 0:
                self.result = 100
                exit_code = testcase.TestCase.EX_OK
            self.stop_time = time.time()

        except KeyError:
            self.__logger.error("Please give cmd as arg. kwargs: %s", kwargs)
        return exit_code
