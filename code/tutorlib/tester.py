import copy
import inspect
from io import StringIO
import os
import sys
import unittest

from tutorlib.streams import redirect_stdin, redirect_stdout, redirect_stderr


STUDENT_LOCALS_NAME = 'student_lcls'
TEST_RESULT_IDENTIFIER = '__test_result'


class StudentTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.standard_output = ''
        self.error_output = ''

    def run_in_student_context(self, f, input_text=''):
        '''
        Execute the given function in the context of the student's code, using
        the provided input_text (if any) as stdin.

        Note that name of the given function will be injected into the student
        context, meaning that it should be unique (ie, things will go terribly
        wrong if you give it the same name as a builtin or as a function which
        the student may reasonably have defined).

        '''
        # create streams
        input_stream = StringIO(input_text or '')
        output_stream = StringIO()
        error_stream = StringIO()

        # we have a function object, f, that we want to execute in a specific
        # context (that of the student's code)
        # ideally, we'd just exec the object with those locals and globals, but
        # there's no built-in support for that in Python (at least that I can
        # find)
        # however, we can easily exec a *string* in a specific context
        # so our 'simple' solution is this: grab the source of the function we
        # want to run and exec *that* in the context of the student code
        lcls = copy.copy(student_lcls)

        function_source = trim_indentation(inspect.getsource(f))
        exec(compile(function_source, '<test_function>', 'exec'), lcls)

        # we now have our function, as an object, in the context of the
        # student code
        # now we need to actually *run* it, and extract the output, in that
        # same context, and again we need a string for that
        function_name = f.__name__
        test_statement = '{} = {}()'.format(
            TEST_RESULT_IDENTIFIER, function_name
        )

        # finally, actually execute that test function, and extract the result
        with redirect_stdin(input_stream), redirect_stdout(output_stream), \
                redirect_stderr(error_stream):
            exec(compile(test_statement, '<test_run>', 'single'), lcls)
            result = lcls[TEST_RESULT_IDENTIFIER]

        self.standard_output = output_stream.getvalue()
        self.error_output = error_stream.getvalue()

        return result


class TutorialTestResult():
    PASS = 'PASS'
    FAIL = 'FAIL'
    ERROR = 'ERROR'
    INDETERMINATE = 'INDETERMINATE'  # main passes, but others fail
    STATUSES = [PASS, FAIL, ERROR, INDETERMINATE]

    def __init__(self, description, status, message, output_text, error_text):
        self.description = description

        self.status = status
        self.message = message

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
            _, e, _ = err

            inner_message = '{}: {}'.format(type(e).__name__, e)
        else:
            inner_message = 'Correct'

        message = construct_header_message(inner_message)

        # build and save our result class
        result = TutorialTestResult(description, status, message,
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

        # NB: if we use exec with separate globals and locals dictionaries,
        # recursive functions will not behave as expected
        # this is due to issues with how exec treats top-level function
        # definitions
        # normally, a function defined at top-level will be placed into locals,
        # *but locals will be globals() at that scope*
        # recursive calls will always search in globals, meaning that if code
        # is execed with separate globals and locals dicts, and top-level
        # function definitions are bound to locals, those functions will not
        # be able to find themselves in globals()
        # see http://stackoverflow.com/a/872082/1103045
        lcls.update(gbls)

        # execute the student's code, and grab a reference to the function
        exec(compile(code_text, 'student_code.py', 'exec'), lcls)

        # inject necessary data into global scope
        inject_to_globals(STUDENT_LOCALS_NAME, lcls)
        inject_to_globals(StudentTestCase.__name__, StudentTestCase)

        # now that we've messed with globals, we must be careful to undo any
        # changes if an error occurs
        try:
            self._run_test(test_class)
        finally:
            # clean up the globals we KNOW we explicitly added
            # leave the ones that might have been there already, and which will
            # do no harm to keep (basically not student code)
            remove_from_globals(STUDENT_LOCALS_NAME)

    def _run_test(self, test_class):
        # load up the tests to run from the class
        tests = [unittest.TestLoader().loadTestsFromTestCase(test_class)]
        suite = unittest.TestSuite(tests)

        # run the tests, but silently
        runner = unittest.TextTestRunner(resultclass=TestResult)

        with open(os.devnull, 'w') as devnull:
            stdout, stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = devnull, devnull  # TODO: this isn't working

            try:
                result = runner.run(suite)
            finally:
                sys.stdout, sys.stderr = stdout, stderr

        assert result.main_result is not None, \
                'Could not detect MAIN_TEST ({})'.format(test_class.MAIN_TEST)

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
            overall_result.message = construct_header_message(
                'Make sure your code also works for similar inputs'
            )
        else:
            overall_result = result.main_result

        self._results[test_class] = overall_result


def indent(text, spaces=4):
    return '\n'.join(' '*spaces + line for line in text.splitlines())


def trim_indentation(text):
    lines = [line for line in text.splitlines() if line.strip()]

    # TODO hacky atm, dunno if it'll work with tabs
    indents = [len(line) - len(line.lstrip()) for line in lines]
    indent = min(indents)

    unindented_text = '\n'.join(line[indent:] for line in text.splitlines())
    return unindented_text + ('\n' if text.splitlines()[-1] == '\n' else '')


def inject_to_globals(name, value):
    assert name not in globals() or globals()[name] == value, \
            'Name {} already exists at global scope'.format(name)
    globals()[name] = value


def remove_from_globals(name):
    assert name in globals(), \
            'Cannot remove non-existent global {}'.format(name)
    del globals()[name]


def construct_header_message(inner_message):
    first_line = inner_message.splitlines()[0]
    header = '-'*len(first_line)
    message = '{0}\n{1}\n{0}\n'.format(header, inner_message)
    return message
