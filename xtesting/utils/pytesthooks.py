import pytest

details = None


def pytest_sessionstart(session):
    global details
    details = dict(tests=[])


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global details
    outcome = yield
    result = outcome.get_result()
    if result.when == 'call':
        if result.outcome == 'passed':
            test = dict(status='PASSED', result=call.result)
        elif result.outcome == 'failed':
            test = dict(status='FAILED', result=call.excinfo)
        elif result.outcome == 'skipped':
            test = dict(status='SKIPPED', result=call.excinfo)
        else:
            test = {}
        details['tests'].append(test)
