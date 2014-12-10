import copy
from io import StringIO
import os
import sys
import unittest

from streams import redirect_stdin, redirect_stdout, redirect_stderr


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


class TestResult(unittest.TestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.successes = []
        self.failures = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)

    def addError(self, test, err):
        super().addError(test, err)
        self.failures.append((test, err))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.failures.append((test, err))


class TutorialTester():
    def __init__(self, test_classes, test_gbls, test_lcls):
        self.test_classes = test_classes
        self.test_gbls = test_gbls
        self.test_lcls = test_lcls

        self.results = {}  # test class : results

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

            result = runner.run(suite)

            sys.stdout, sys.stderr = stdout, stderr  # TODO: finally?

        # for now, pass iff all pass
        # TODO: need to identify main test (the one in the description)


def indent(text, spaces=4):
    return '\n'.join(' '*spaces + line for line in text.splitlines())


def inject_to_globals(name, value):
    assert name not in globals(), \
            'Name {} already exists at global scope'.format(name)
    globals()[name] = value
