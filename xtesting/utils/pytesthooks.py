import pytest

details = None
passed = None
failed = None
result = None


def pytest_sessionstart(session):
    global details, passed, failed, result
    details = dict(tests=[])
    passed = 0
    failed = 0
    result = 0


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global details, passed, failed, result
    yreport = yield
    report = yreport.get_result()
    if report.when == 'call':
        test = dict(name=report.nodeid, status=report.outcome.upper())
        if report.passed:
            passed += 1
        elif report.failed:
            failed += 1
            test['failure'] = report.longreprtext
        if passed + failed:
            result = passed / (passed + failed) * 100
        details['tests'].append(test)
