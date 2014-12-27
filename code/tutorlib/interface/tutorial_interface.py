import sys

from tutorlib.interface.alarm import Alarm
from tutorlib.interface.tutorial import Tutorial
from tutorlib.interface.web_api import WebAPI
from tutorlib.testing.tester import TutorialTester


class TutorialInterface():
    def __init__(self):
        # web communications
        self.web_api = WebAPI()

        # tutorial details
        self.tutorial = None
        self.num_checks = 0
        self.next_hint_index = 0

        # gui callbacks / communication
        self.editor = None

        self.user = None
        self.solved = False

    # web communications
    def set_url(self, url):
        self.web_api.url = url  # TODO: consider the point of this method

    # tutorial details
    def load_data(self, filename, problem_name):
        self.solved = False
        self.num_checks = 0
        self.next_hint_index = 0

        self.tutorial = Tutorial(problem_name, filename)

    def get_hints(self):
        return self.tutorial.hints  # TODO: why do both this and the next method exist?

    def get_next_hint(self):
        try:
            hint = self.tutorial.hints[self.next_hint_index]
        except IndexError:
            return None

        self.next_hint_index += 1

        html = '<p>\n<b>Hint {}: </b>{}'.format(self.next_hint_index, hint)
        return html

    def get_preloaded(self):
        return self.tutorial.preload_code_text

    def get_text(self):
        return self.tutorial.description

    def get_short_description(self):
        return self.tutorial.short_description

    # gui callbacks / communication
    def set_editor(self, editor):
        self.editor = editor

    def reset_editor(self, answer_file):
        self.editor.reset(answer_file, self.tutorial.preload_code_text)

    # tests
    def run_tests(self, text):
        alarm = Alarm(self.tutorial.timeout)
        alarm.setDaemon(True)
        alarm.start()

        try:
            return self._runtests(text)
        except KeyboardInterrupt as e:
            print('Timeout - possible infinite loop', file=sys.stderr)
            return None, None
        finally:
            alarm.stop_interrupt()

    def _runtests(self, text):
        self.num_checks += 1

        # load the support file (giving students access to functions, variables
        # etc which they may need for their solution)
        gbls, lcls = self.tutorial.exec_submodule(Tutorial.SUPPORT_MODULE)

        # perform the static analysis
        # this should only take place if there are no errors in parsing the
        # student's code (as those would interfere with ast)
        # we therefore collect those first, and only proceed if there were
        # no such errors
        # note that we may have an error with no line information (this will be
        # the case with a NameError, for example)
        analyser = self.tutorial.analyser
        tester = TutorialTester(self.tutorial.test_classes, gbls, lcls)

        error_line = analyser.check_for_errors(text)
        if error_line is not None:
            self.editor.error_line(error_line)

        if not analyser.errors:
            # there were no errors, so it's safe to perform the analysis
            analyser.analyse(text)

            # we can likewise run the tests
            tester.run(text, self.tutorial.student_function_name)

        return tester, analyser
