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
    """
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

    Args:
      path (str): The path of the module to execute.
      gbls (dict, optional): The globals dictionary to use.  Defaults to None.
      lcls (dict, optional): The locals dictionary to use.  Defaults to None.
          If both gbls and lcls are None, then lcls will *not* be initialised
          to be the same dictionary as gbls.

    Returns:
      The globals and locals dictionaries, as updated by executing the module.

      If gbls and/or lcls were provided as arguments, those same dictionaries
      will be returned here.

    Raises:
      AssertionError: If lcls is provided, but gbls is not.  This is an error
          condition because it will almost certainly lead to unexpected results
          when calling exec, which does not accept keyworod arguments and so
          must be provided with a new (empty) gbls dict.  If the intention is
          to capture all variablees in the one dict, only gbls should be given.

    """
    assert lcls is None or gbls is not None, \
            'exec_module was called with a locals dictionary, but no globals' \
            'dictionary. This behaviour is not sensibly supported by exec, ' \
            'and so is considered an error condition.'

    if gbls is None:
        gbls = {}
    if lcls is None:
        lcls = {}

    with open(path) as f:
        exec(compile(f.read(), path, 'exec'), gbls, lcls)

    return gbls, lcls


class Tutorial():
    """
    A representation of a single tutorial problem.

    Class Attributes:
      ANALYSIS_MODULE (constant): The name of the static analysis file within
          the tutorial package.
      CONFIG_MODULE (constant): The name of the configuration file within the
          tutorial package.
      PRELOAD_MODULE (constant): The name of the file containing code to
          display to the student when first loading the tutorial.
      SUPPORT_MODULE (constant): The name of the file containing code to
          execute prior to running the student code.
      TESTS_MODULE (constant): The name of the unit tests file within the
          tutorial package.
      SUBMODULES ([constant]): A list of all package submodule names.

      DESCRIPTION_FILE (constant): The name of the tutorial description file.
      FILES ([constant]): A list of all files, other than modules, in the
          tutorial package.

      TESTS_VARIABLE_NAME (constant): The name of the variable declared in
          TESTS_MODULE which will contain a list of test classes to use.
      ANALYSIS_VARIABLE_NAME (constant): The name of the variable decalred in
          ANALYSIS_MODULE which will contain the analyser to use.

    Attributes:
      name (str): The name of the tutorial.
      short_description (str): A short description of the tutorial problem.
      hints ([str]): All hints for this tutorial.

      answer_path (str): The path to the student's answer (on the local disk).
      tutorial_path (str): The path of the tutorial package (.tut directory).

      timeout (int): Maximum run time of the tutorial code, in seconds.
      wrap_student_code (bool): Whether the student code for this tutorial will
          need to be wrapped in a function before being run.  (This will be
          necessary wherever the student is not required to declare any
          functions.)

    """
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
        """
        Initialise a new Tutorial object.

        Args:
          name (str): The name of the tutorial.
          tutorial_path (str): The path of the tutorial package (.tut
              directory).  This must exist and contain the correct files.
          answer_path (str): The path to the student's answer (on the local
              disk).  This need not exist yet.

        """
        self.name = name
        self.tutorial_path = tutorial_path
        self.answer_path = answer_path

        # load the description
        self.description = self.read_file(Tutorial.DESCRIPTION_FILE)

        # parse the config file
        _, config_lcls = self.exec_submodule(Tutorial.CONFIG_MODULE)

        self.short_description = config_lcls.get('SHORT_DESCRIPTION', '')
        self.wrap_student_code = config_lcls.get('WRAP_STUDENT_CODE', False)
        self.timeout = config_lcls.get('TIMEOUT', 1)

        self.hints = config_lcls.get('HINTS', [])
        self._next_hint_index = 0

        # initial values for lazy properties
        self._preload_code_text = None

    def _get_answer_hash(self):
        with open(self.answer_path) as f:
            data = f.read().encode('utf8')
            return sha512(data).digest()

    def _get_answer_mtime(self):
        return os.path.getmtime(self.answer_path)

    @property
    def answer_info(self):
        """
        Return the hash and modification time of the local answer file.

        Returns:
          A two-element tuple conttaining the answer information.
          The first element of the tuple is the hash of the current contents
          of the student's answer.
          The second element of the tuple is the modification time of the local
          answer file (as a unix time -- this is supported on Windows).

          If no answer file exists, both elements will be None.

        """
        if not os.path.exists(self.answer_path):
            return None, None
        return self._get_answer_hash(), self._get_answer_mtime()

    @property
    def has_answer(self):
        """
        Return whether a local answer exsits to this tutorial.

        """
        return os.path.exists(self.answer_path)

    @property
    def hash(self):
        """
        Return a hash of the entire tutorial problem (.tut directory).

        This is defined as a hash of the string comprised of the contents of
        each submodule and other file (in that order) in the package.

        Each required submodule and file must actually exist.

        Returns:
          A sha512 hash of the tutorial problem, according to the above rules.

        """
        hash_obj = sha512()

        for module_name in self.SUBMODULES:
            text = self.read_submodule(module_name).encode('utf8')
            hash_obj.update(text)

        for file_name in self.FILES:
            text = self.read_file(file_name).encode('utf8')
            hash_obj.update(text)

        return hash_obj.digest()

    def _assert_valid_file(self, file_name):
        """
        Assert that the given filename exists in the tutorial package.

        Args:
          file_name (str): The name of the file to check.

        Raises:
          AssertionError: If the file is not present.

        """
        assert os.path.exists(self.tutorial_path) \
                and file_name in os.listdir(self.tutorial_path), \
                'Invalid .tut package: missing {}'.format(file_name)

    def _assert_valid_module(self, module_name):
        """
        Assert that the given module exists in the tutorial package.

        Args:
          module_name (str): The name of the module to check.

        Raises:
          AssertionError: If the module is not present, or if the requested
              module is not a valid module name for a tutorial package.

        """
        assert module_name in Tutorial.SUBMODULES, \
            'Unknown submodule: {}'.format(module_name)

        self._assert_valid_file(module_name)

    def exec_submodule(self, module_name, gbls=None, lcls=None):
        """
        Execute the given submodule, and return the resulting globals and
        locals dictionaries.

        The submodule must exist and be valid.

        Args:
          module_name (str): The name of the module to execute.
          gbls (dict, optional): The globals dictionary to use, if any.
              Defaults to None.
          lcls (dict, optional): The locals dictionary to use, if any.
              Defaults to None.

        Returns:
          The globals and locals dictionaries, as updated by executing the
          module, or new dictionaries if none were provided.

        """
        self._assert_valid_module(module_name)
        path = os.path.join(self.tutorial_path, module_name)

        return exec_module(path, gbls=gbls, lcls=lcls)

    def read_submodule(self, module_name):
        """
        Read and return the text of the given submodule.

        The submodule must exist and be valid.

        Args:
          module_name (str): The name of the module to read.

        Returns:
          A string containing the full text of the module file.

        """
        self._assert_valid_module(module_name)
        path = os.path.join(self.tutorial_path, module_name)

        with open(path) as f:
            return f.read()

    def read_file(self, file_name):
        """
        Read and return the text of the given file.
        :param file_name:
        :return:
        """
        assert file_name in self.FILES  # TODO: can't quite merge into the below call, because that's used from _assert_valid_module
        self._assert_valid_file(file_name)
        path = os.path.join(self.tutorial_path, file_name)

        with open(path) as f:
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
