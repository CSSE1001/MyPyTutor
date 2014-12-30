import ast
from hashlib import sha512
import os

from tutorlib.analysis.analyser import CodeAnalyser
from tutorlib.analysis.visitor import TutorialNodeVisitor
from tutorlib.testing.cases import StudentTestCase

# keep PEP8 happy
# these imports are indirectly used in Tutorial, and must not be removed
ast = ast
CodeAnalyser = CodeAnalyser
TutorialNodeVisitor = TutorialNodeVisitor
StudentTestCase = StudentTestCase


def exec_module(path, gbls=None, lcls=None):
    '''
    Execute the module at the given path using the provided globals and locals

    NB: Here be massive, fire-breathing dragons.
        The main reason for this is that the module code itself may rely on
        references within its own locals/globals dictionaries.
        It may therefore be an error to make use of specific references from
        these dictionaries without also bringing other, related references
        into the calling context.

        A simple example helps illustrate this.
        Take the following module definition:
          # module.py
          class A():
              pass
          class B():
              def f(self):
                  a = A()  ## -- mark

        When executed, that module will define A and B in locals.
        If we extract B alone, ie B = locals['B'], and then run it in a context
        where A is not defined, then we will get a NameError on the line
        marked above.

        To avoid this, we need to also extract A into a scope that B can see.
    '''
    if gbls is None:
        gbls = {}
    if lcls is None:
        lcls = {}

    with open(path) as f:
        exec(compile(f.read(), path, 'exec'), gbls, lcls)

    return gbls, lcls


class Tutorial():
    ANALYSIS_MODULE = 'analysis.py'
    CONFIG_MODULE = 'config.py'
    PRELOAD_MODULE = 'preload.py'
    SUPPORT_MODULE = 'support.py'
    TESTS_MODULE = 'tests.py'
    SUBMODULES = [
        ANALYSIS_MODULE,
        CONFIG_MODULE,
        PRELOAD_MODULE,
        SUPPORT_MODULE,
        TESTS_MODULE,
    ]

    DESCRIPTION_FILE = 'description.html'
    FILES = [
        DESCRIPTION_FILE,
    ]

    TESTS_VARIABLE_NAME = 'TEST_CLASSES'
    ANALYSIS_VARIABLE_NAME = 'ANALYSER'

    def __init__(self, name, tutorial_path, answer_path):
        self.name = name
        self.tutorial_path = tutorial_path
        self.answer_path = answer_path

        # load the description
        self._assert_valid_file(Tutorial.DESCRIPTION_FILE)
        description_path = os.path.join(
            self.tutorial_path, Tutorial.DESCRIPTION_FILE
        )
        with open(description_path, 'rU') as f:
            self.description = f.read()

        # parse the config file
        _, config_lcls = self.exec_submodule(Tutorial.CONFIG_MODULE)

        self.short_description = config_lcls.get('SHORT_DESCRIPTION', '')
        self.wrap_student_code = config_lcls.get('WRAP_STUDENT_CODE', False)
        self.timeout = config_lcls.get('TIMEOUT', 1)

        self.hints = config_lcls.get('HINTS', [])
        self._next_hint_index = 0

        # initial values for lazy properties
        self._preload_code_text = None

        # store the answer hash so we can check for answers later
        self.update_answer_hash()

    def _get_answer_hash(self):
        if os.path.exists(self.answer_path):
            with open(self.answer_path) as f:
                data = f.read().encode('utf8')
                return sha512(data).digest()
        return None

    def update_answer_hash(self):
        self._answer_hash = self._get_answer_hash()

    @property
    def answer_has_changed(self):
        return self._get_answer_hash() != self._answer_hash

    def _assert_valid_file(self, file_name):
        assert os.path.exists(self.tutorial_path) \
                and file_name in os.listdir(self.tutorial_path), \
                'Invalid .tut package: missing {}'.format(file_name)

    def _assert_valid_module(self, module_name):
        assert module_name in Tutorial.SUBMODULES, \
            'Unknown submodule: {}'.format(module_name)

        self._assert_valid_file(module_name)

    def exec_submodule(self, module_name, gbls=None, lcls=None):
        self._assert_valid_module(module_name)
        path = os.path.join(self.tutorial_path, module_name)

        return exec_module(path, gbls=gbls, lcls=lcls)

    def read_submodule(self, module_name):
        self._assert_valid_module(module_name)
        path = os.path.join(self.tutorial_path, module_name)

        with open(path, 'rU') as f:
            return f.read()

    # TODO: it's debateable whether these should be properties, as their state
    # TODO: will not persit across calls (due to the re-exec of the module)
    @property
    def test_classes(self):
        # the test module requires access to StudentTestCase, as that's what
        # it will have inherited from
        # because we imported that here, we can just pass in our globals
        _, test_lcls = self.exec_submodule(Tutorial.TESTS_MODULE, globals())

        assert Tutorial.TESTS_VARIABLE_NAME in test_lcls, \
            'Invalid .tut package: {} has no member {}'.format(
                Tutorial.TESTS_MODULE, Tutorial.TESTS_VARIABLE_NAME
            )

        return test_lcls[Tutorial.TESTS_VARIABLE_NAME]

    @property
    def analyser(self):
        # the analysis module requires access to CodeAnalyser, as that's what
        # it must inherit from
        # because we imported that class in this file, we can just pass in
        # our globals() dict
        _, analysis_lcls = self.exec_submodule(Tutorial.ANALYSIS_MODULE,
                                               globals())

        assert Tutorial.ANALYSIS_VARIABLE_NAME in analysis_lcls, \
            'Invalid .tut package: {} has no member {}'.format(
                Tutorial.ANALYSIS_MODULE, Tutorial.ANALYSIS_VARIABLE_NAME
            )

        return analysis_lcls[Tutorial.ANALYSIS_VARIABLE_NAME]

    @property
    def preload_code_text(self):
        if self._preload_code_text is None:
            self._preload_code_text = self.read_submodule(
                Tutorial.PRELOAD_MODULE
            )

        return self._preload_code_text

    @property
    def next_hint(self):
        try:
            hint = self.hints[self._next_hint_index]
        except IndexError:
            return None

        self._next_hint_index += 1
        return hint
