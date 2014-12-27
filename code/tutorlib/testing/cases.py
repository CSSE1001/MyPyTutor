import copy
import inspect
from io import StringIO
import unittest

from tutorlib.testing.streams \
        import redirect_stdin, redirect_stdout, redirect_stderr
from tutorlib.testing.support import trim_indentation

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
        assert STUDENT_LOCALS_NAME in globals(), \
                'Could not find {} in globals()'.format(STUDENT_LOCALS_NAME)
        student_lcls = globals()[STUDENT_LOCALS_NAME]
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
