import traceback
import unittest

from tutorlib.testing.support import StudentTestError, construct_header_message


class TutorialTestResult():
    """
    A class containing information about running a particular StudentTestCase.

    Class Attributes:
      NOT_RUN (constant): The test was not run.
      PASS (constant): The test passed.
      FAIL (constant): The test failed.
      ERROR (constant): An error was encountered when running the test.
      INDETERMINATE (constant): The main test for the test case passed, but
          at least one other test on the test case failed or caused an error.
      STATUSES (constant): An exhaustive list of possible test statuses.

    Attributes:
      description (str): The description of the test.
      status (str): The result of the test.  One of STATUSES.
      output_text (str): The output text of the test (stdout).
      error_text (str): The error text of the test (stderr).

    """
    NOT_RUN = 'NOT_RUN'
    PASS = 'PASS'
    FAIL = 'FAIL'
    ERROR = 'ERROR'
    INDETERMINATE = 'INDETERMINATE'
    STATUSES = [NOT_RUN, PASS, FAIL, ERROR, INDETERMINATE]

    def __init__(self, description, status, exception, output_text='',
                error_text=''):
        """
        Initialise a new TutorialTestResult object.

        Args:
          description (str): The description of the test.
          status (str): The status (result) of the test.  Must be one of the
              elements of STATUSES.
          exception (Exception): The exception encountered when running the
              test, if any.  If no exception was encountered, pass None.
          output_text (str, optional): The contents of stdout for the test.
              Defaults to an empty string.
          error_text (str, optional): The contents of stderr for the test.
              Defaults to an empty string.

        """
        self.description = description

        self.status = status
        self._exception = exception

        self.output_text = output_text
        self.error_text = error_text

    @property
    def exception(self):
        """
        Return the exception encountered when running the test, if any.

        Returns:
          The exception encountered when running the test.
          If the test failed, this will be an AssertionError.
          If no exception was encountered, this will be None.

        """
        return self._exception

    @exception.setter
    def exception(self, value):
        """
        Set the exception encountered when running the test.

        It is an error to try to overwrite an existing exception.

        Args:
          value (Exception): The exception to set.

        """
        assert self._exception is None, \
                'An exception already exists for this test.  ' \
                'A new exception cannot be set.  ' \
                'The existing exception is: {!r}'.format(self._exception)
        self._exception = value

    @property
    def message(self):
        """
        Return the message to display as the result of this test.

        This will be formatted as a header message.

        Returns:
          A header message, containing either 'Correct!', if no exception was
          raised in running the test, or else the string form of the exception.

        """
        if self._exception is None:
            message = 'Correct!'
        else:
            message = str(self._exception)

        return construct_header_message(message)

    @property
    def status(self):
        """
        Return the status of the test.  This will be one of STATUSES.

        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Set the status of the test.

        It is an error to attempt to set the status to a value that is not
        one of STATUSES.

        Args:
          status (str): The status to set.  Must be one of STATUSES.

        """
        assert status in TutorialTestResult.STATUSES, \
            'status must be one of {}'.format(TutorialTestResult.STATUSES)
        self._status = status


class TestResult(unittest.TestResult):
    """
    A custom unittest.TestResult subclass for testing subclasses of
    StudentTestCase.

    This class relies on several class attributes of StudentTestCase, and so
    is unsuitable for generic unittest.TestCase subclasess.

    Attributes:
      results ([TutorialTestResult]): The results of the test.
      main_result (TutorialTestResult): The result for the main test case.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.results = []
        self.main_result = None

    def _addResult(self, test, status, err=None):
        """
        Add the given result for the given test.

        This method relies heavily on class attributes of StudentTestCase.

        Args:
          test (StudentTestCase): The test to add the result for.
          status (constant): The result status.  Must be one of the elements
              of TutorialTestResult.STATUSES.
          err (tuple, optional): The error information, if any.  This is in
              the same format as for unittest.TestResult.add{Error,Failure}.

        Raises:
          AssertionError: If expected StudentTestCase attributes are not found
              on the given test.

        """
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
            _, line_number, _, _ = traceback.extract_tb(e.__traceback__)[-1]
            exception = StudentTestError(str(e), line_number)
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
