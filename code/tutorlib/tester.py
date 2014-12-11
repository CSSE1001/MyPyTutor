import copy
from io import StringIO
import os
import sys
import unittest

from tutorlib.streams import redirect_stdin, redirect_stdout, redirect_stderr


TEST_FUNCTION_NAME = 'student_function'


class StudentTestCase(unittest.TestCase):
    def run_student_code(self, *args, input_text='', **kwargs):
        # create streams
        input_stream = StringIO(input_text or '')
        output_stream = StringIO()
        error_stream = StringIO()

        # execute student code with redirected streams
        # NB: this assumes that student_function is accessible
        with redirect_stdin(input_stream), redirect_stdout(output_stream), \
                redirect_stderr(error_stream):
            result = student_function(*args, **kwargs)

        self.standard_output = output_stream.getvalue()
        self.error_output = error_stream.getvalue()

        return result


class TutorialTestResult():
    PASS = 'PASS'
    FAIL = 'FAIL'
    ERROR = 'ERROR'
    INDETERMINATE = 'INDETERMINATE'  # main passes, but others fail
    STATUSES = [PASS, FAIL, ERROR, INDETERMINATE]

    def __init__(self, description, status, output_text, error_text):
        self.description = description

        self.status = status

        self.output_text = output_text
        self.error_text = error_text

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

    def _addResult(self, test, status):
        assert hasattr(test, 'DESCRIPTION'), \
                'Test case {} is missing DESCRIPTION attr'.format(test)
        description = test.DESCRIPTION

        assert hasattr(test, 'standard_output') \
                and hasattr(test, 'error_output'), \
                'Missing output attrs on {} in test {} (got {})'.format(
                    test, test.id(), dir(test)
                )
        output_text = test.standard_output
        error_text = test.error_output

        result = TutorialTestResult(description, status, output_text,
                                    error_text)
        self.results.append(result)

        # TODO: determine MAIN_TEST (need to check test output)
        # TODO: this is hacky, and won't work (as it's using substrings)
        assert hasattr(test, 'MAIN_TEST'), \
                'Test case {} is missing MAIN_TEST attr'.format(test)
        if test.MAIN_TEST in test.id():
            self.main_result = result

    def addSuccess(self, test):
        super().addSuccess(test)
        self._addResult(test, TutorialTestResult.PASS)

    def addError(self, test, err):
        super().addError(test, err)
        self._addResult(test, TutorialTestResult.ERROR)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._addResult(test, TutorialTestResult.FAIL)


class TutorialTester():
    def __init__(self, test_classes, test_gbls, test_lcls):
        self.test_classes = test_classes
        self.test_gbls = test_gbls
        self.test_lcls = test_lcls

        self._results = {}  # test class : results

    @property
    def results(self):
        '''
        Test results, in the same order as the test classes
        '''
        return [self._results[cls] for cls in self.test_classes]

    def run(self, code_text, student_function_name):
        # if no function name is given, we need to wrap their code
        if student_function_name is None:
            # TODO: this will cause problems with line detection for errors
            # TODO: should probably intercept and modify exceptions
            student_function_name = '_function_under_test'
            code_text = 'def {}():\n{}'.format(
                student_function_name, indent(code_text)
            )

        for test_class in self.test_classes:
            self.run_test(test_class, code_text, student_function_name)

    def run_test(self, test_class, code_text, student_function_name):
        # grab a copy of our context to use
        # unfortunately, it's not robust to copy globals(), which means we
        # can't grab a nice deepcopy of test_gbls
        # in other words, if students mess with that, all future tests will be
        # inconsistent :(
        gbls = copy.copy(self.test_gbls)
        try:
            lcls = copy.deepcopy(self.test_lcls)
        except:
            lcls = copy.copy(self.test_lcls)

        # execute the student's code, and grab a reference to the function
        exec(compile(code_text, 'student_code.py', 'exec'), gbls, lcls)
        assert student_function_name in lcls, 'Student function not defined!'
        # TODO: that is NOT an assertion failure; it will happen in normal use
        # TODO: the assertion is merely there for testing atm
        student_function = lcls[student_function_name]

        # inject necessary data into global scope
        inject_to_globals(TEST_FUNCTION_NAME, student_function)
        inject_to_globals(StudentTestCase.__name__, StudentTestCase)

        # load up the tests to run from the class
        tests = [unittest.TestLoader().loadTestsFromTestCase(test_class)]
        suite = unittest.TestSuite(tests)

        # run the tests, but silently
        runner = unittest.TextTestRunner(resultclass=TestResult)

        with open(os.devnull, 'w') as devnull:
            stdout, stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = devnull, devnull

            try:
                result = runner.run(suite)
            finally:
                sys.stdout, sys.stderr = stdout, stderr

        # collapse the results
        # four possible situations
        #   * all tests pass
        #       -- keep MAIN_TEST
        #   * main test passes, but others fail
        #       -- adjust MAIN_TEST to reflect this
        #   * main test fails, but others pass
        #       -- keep failure
        #   * all tests fail
        #       -- keep failure
        if all(r.status == TutorialTestResult.PASS for r in result.results):
            overall_result = result.main_result
        elif result.main_result.status == TutorialTestResult.PASS:
            overall_result = result.main_result
            overall_result.status = TutorialTestResult.INDETERMINATE
        else:
            overall_result = result.main_result

        self._results[test_class] = overall_result

        # clean up the globals we KNOW we explicitly added
        # leave the ones that might have been there already, and which will
        # do no harm to keep (basically not student code)
        remove_from_globals(TEST_FUNCTION_NAME)


def indent(text, spaces=4):
    return '\n'.join(' '*spaces + line for line in text.splitlines())


def inject_to_globals(name, value):
    assert name not in globals() or globals()[name] == value, \
            'Name {} already exists at global scope'.format(name)
    globals()[name] = value


def remove_from_globals(name):
    assert name in globals(), \
            'Cannot remove non-existent global {}'.format(name)
    del globals()[name]