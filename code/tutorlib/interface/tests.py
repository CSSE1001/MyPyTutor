from tutorlib.interface.alarm import Alarm
from tutorlib.interface.tutorial import Tutorial
from tutorlib.testing.tester import TutorialTester


class StudentCodeError(Exception):
    """
    An exception raised in student code, for which the problem line can be
    identified.  This includes, inter alia, SyntaxErrors.

    Attributes:
      message (str): The exception message.
      linenum (int): The line of the error in the student's code.

    """
    def __init__(self, message, linenum):
        super().__init__(message)
        self.linenum = linenum


def run_tests(tutorial, text):
    """
    Run the tests for the given tutorial.

    This function uses an Alarm object to prevent infinite loops from causing
    MyPyTutor to hand.

    Args:
      tutorial (Tutorial): The tutorial to run the tests for.
      text (str): The student's code.

    Returns:
      A two-element tuple.

      The first element in the tuple will be the TutorialTester object which
      was run on the student's code.

      The second element in the tuple will be the CodeAnalyser object which was
      run on the student's code.

      If execution of the student's code times out, None will be returned for
      both elements.

    Raises:
      StudentCodeError: If an error is encountered when compiling the
          student's code.

    """
    alarm = Alarm(tutorial.timeout)
    alarm.setDaemon(True)
    alarm.start()

    try:
        return _run_tests(tutorial, text)
    except KeyboardInterrupt as e:
        return None, None
    finally:
        alarm.stop_interrupt()


def _run_tests(tutorial, text):
    """
    Run the tests for the given tutorial.

    Testing and analysis will only be performed if no compilation errors were
    encountered when executing the student's code.

    Args:
      tutorial (Tutorial): The tutorial to run the tests for.
      text (str): The student's code.

    Returns:
      A two-element tuple.

      The first element in the tuple will be the TutorialTester object which
      was run on the student's code.

      The second element in the tuple will be the CodeAnalyser object which was
      run on the student's code.

      If execution of the student's code times out, None will be returned for
      both elements.

    Raises:
      StudentCodeError: If an error is encountered when compiling the
          student's code.

    """
    # load the support file (giving students access to functions, variables
    # etc which they may need for their solution)
    gbls, lcls = tutorial.exec_submodule(Tutorial.SUPPORT_MODULE)

    # perform the static analysis
    # this should only take place if there are no errors in parsing the
    # student's code (as those would interfere with ast)
    # we therefore collect those first, and only proceed if there were
    # no such errors
    # note that we may have an error with no line information (this will be
    # the case with a NameError, for example)
    analyser = tutorial.analyser
    tester = TutorialTester(tutorial.test_classes, gbls, lcls)

    error_line = analyser.check_for_errors(text)
    if error_line is not None:
        raise StudentCodeError('Exception in student code', error_line)

    if not analyser.errors:
        # there were no errors, so it's safe to perform the analysis
        analyser.analyse(text)

        # we can likewise run the tests
        tester.run(text, tutorial.wrap_student_code)

    return tester, analyser
