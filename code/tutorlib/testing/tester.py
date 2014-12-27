import copy
import os
import sys
import unittest

import tutorlib.testing.cases
from tutorlib.testing.cases import StudentTestCase, STUDENT_LOCALS_NAME
from tutorlib.testing.results import TestResult, TutorialTestResult
from tutorlib.testing.support \
        import StudentTestError, construct_header_message, indent, \
               inject_to_module, remove_from_module


class TutorialTester():
    def __init__(self, test_classes, test_gbls, test_lcls):
        self.test_classes = test_classes
        self.test_gbls = test_gbls
        self.test_lcls = test_lcls

        # initialise our results dict
        status = TutorialTestResult.NOT_RUN
        message = construct_header_message('Error in code: test not run')

        self._results = {
            cls: TutorialTestResult(cls.DESCRIPTION, status, message)
            for cls in self.test_classes
        }

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
            self.run_test(test_class, code_text, student_function_name)  # TODO: remove student_function_name (now unnecessary)

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
        lcls = dict(gbls, **lcls)

        # execute the student's code, and grab a reference to the function
        exec(compile(code_text, 'student_code.py', 'exec'), lcls)

        # inject necessary data into global scope
        inject_to_module(tutorlib.testing.cases, STUDENT_LOCALS_NAME, lcls)

        this = sys.modules[__name__]  # relable black magic ;)
        inject_to_module(this, StudentTestCase.__name__, StudentTestCase)

        # now that we've messed with globals, we must be careful to undo any
        # changes if an error occurs
        try:
            self._run_test(test_class)
        finally:
            # clean up the globals we KNOW we explicitly added
            # leave the ones that might have been there already, and which will
            # do no harm to keep (basically not student code)
            remove_from_module(tutorlib.testing.cases, STUDENT_LOCALS_NAME)

    def _run_test(self, test_class):
        # load up the tests to run from the class
        tests = [unittest.TestLoader().loadTestsFromTestCase(test_class)]
        suite = unittest.TestSuite(tests)

        # run the tests, but silently
        with open(os.devnull, 'w') as devnull:
            runner = unittest.TextTestRunner(
                resultclass=TestResult,
                stream=devnull,
            )
            result = runner.run(suite)

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
            overall_result.exception = StudentTestError(
                'Make sure your code also works for similar inputs'
            )
        else:
            overall_result = result.main_result

        self._results[test_class] = overall_result
