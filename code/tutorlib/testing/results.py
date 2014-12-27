import unittest

from tutorlib.testing.support import construct_header_message


class TutorialTestResult():
    NOT_RUN = 'NOT_RUN'
    PASS = 'PASS'
    FAIL = 'FAIL'
    ERROR = 'ERROR'
    INDETERMINATE = 'INDETERMINATE'  # main passes, but others fail
    STATUSES = [NOT_RUN, PASS, FAIL, ERROR, INDETERMINATE]

    def __init__(self, description, status, exception, output_text='',
                 error_text=''):
        self.description = description

        self.status = status
        self._exception = exception

        self.output_text = output_text
        self.error_text = error_text

    @property
    def exception(self):
        return self._exception

    @exception.setter
    def exception(self, value):
        self._exception = value

    @property
    def message(self):
        if self._exception is None:
            message = 'Correct!'
        else:
            message = str(self._exception)

        return construct_header_message(message)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        assert status in TutorialTestResult.STATUSES, \
            'status must be one of {}'.format(TutorialTestResult.STATUSES)
        self._status = status


class TestResult(unittest.TestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.results = []
        self.main_result = None

    def _addResult(self, test, status, err=None):
        # get the description of the test
        assert hasattr(test, 'DESCRIPTION'), \
            'Test case {} is missing DESCRIPTION attr'.format(test)
        description = test.DESCRIPTION

        # get stdout and stderr (saved by StudentTestCase)
        assert hasattr(test, 'standard_output') \
                and hasattr(test, 'error_output'), \
            'Missing output attrs on {} in test {} (got {})'.format(
                test, test.id(), dir(test)
        )
        output_text = test.standard_output
        error_text = test.error_output

        # generate the test message
        if err is not None:
            _, exception, _ = err
        else:
            exception = None

        # build and save our result class
        result = TutorialTestResult(description, status, exception,
                                    output_text, error_text)
        self.results.append(result)

        # determine if this is the MAIN_TEST
        # this relies upon the implementation of id(), but I'm not aware of
        # a better way of doing this
        assert hasattr(test, 'MAIN_TEST'), \
            'Test case {} is missing MAIN_TEST attr'.format(test)
        function_name = test.id().split('.')[-1]
        if test.MAIN_TEST == function_name:
            self.main_result = result

    def addSuccess(self, test):
        super().addSuccess(test)
        self._addResult(test, TutorialTestResult.PASS)

    def addError(self, test, err):
        super().addError(test, err)
        self._addResult(test, TutorialTestResult.ERROR, err)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._addResult(test, TutorialTestResult.FAIL, err)
