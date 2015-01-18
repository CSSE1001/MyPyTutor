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
          If both gbls and lcls are None, then lcls will not be initialised at
          all; exec will be run with just a single argument.

    Returns:
      The globals and locals dictionaries, as updated by executing the module.

      If lcls was None, then gbls will be returned twice.

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
    # see http://bugs.python.org/issue991196
    #
    # NB: really importantly, we *cannot* attempt to merge gbls and lcls
    # *after* exec has been run, as it's too late then; the binding has
    # already happened
    # as a result, we *must* have two cases here; either we are passing in
    # both dictionaries, or we're only passing only one
    # this is the same reason that we initialise lcls to gbls where possible
    if gbls is None:
        gbls = {}

    with open(path) as f:
        if lcls is None:
            exec(compile(f.read(), path, 'exec'), gbls)
        else:
            exec(compile(f.read(), path, 'exec'), gbls, lcls)

    if lcls is None:
        lcls = gbls

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

        # initial values for lazy properties
        self._preload_code_text = None

    def _get_answer_hash(self):
        """
        Return the hash of the local answer file.

        This assumes that the answer file exists.

        Returns:
          The sha512 hash of the contents of the answer file.

        """
        with open(self.answer_path) as f:
            data = f.read().encode('utf8')
            return sha512(data).digest()

    def _get_answer_mtime(self):
        """
        Return the modification time of the local answer file.

        This assumes that the answer file exists.

        Returns:
          The modification time of the answer file, as a unix timestamp.

        """
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

        Args:
          file_name (str): The name of the file to read.

        Returns:
          A string containing the full text of the file.

        """
        # self._assert_valid_file is called from self._assert_valid_module,
        # and so it cannot check in self.FILES
        assert file_name in self.FILES
        self._assert_valid_file(file_name)
        path = os.path.join(self.tutorial_path, file_name)

        with open(path) as f:
            return f.read()

    @property
    def test_classes(self):
        """
        Return the StudentTestCase subclasses that should be used to test the
        student's code.

        The result of this property is not cached, and new (distinct) class
        objects will be returned on successive calls.

        The subclasses are found by executing the TESTS_MODULE, and reading out
        the appropriate variable from the resulting locals dictionary.

        StudentTestCase must be accessible in the globals() dict of the current
        module, as it is passed to the submodule during execution.

        The submodule must define a variable called TESTS_VARIABLE_NAME.

        Returns:
          A list of StudentTestCase subclasses to test the student's code with.
          Note that this is a list of the class objects, not of instances.

        """
        assert globals().get('StudentTestCase') is not None
        _, test_lcls = self.exec_submodule(Tutorial.TESTS_MODULE, globals())

        assert Tutorial.TESTS_VARIABLE_NAME in test_lcls, \
            'Invalid .tut package: {} has no member {}'.format(
                Tutorial.TESTS_MODULE, Tutorial.TESTS_VARIABLE_NAME
            )

        return test_lcls[Tutorial.TESTS_VARIABLE_NAME]

    @property
    def analyser(self):
        """
        Return the CodeAnalyser subclass that should be used to analyse the
        student's code.

        The result of this property is not cached, and a new CodeAnalyser
        instance will be returned on each successive call.

        The analyser is found by executing the ANALYSIS_MODULE, and reading out
        the appropraite variable from the resulting locals dictionary.

        ast, CodeAnalyser, and TutorialNodeVisitor must all be accessible in
        the globals() dict of the current module, as it is passed to the
        submodule during execution.

        The submodule must define a variable called ANALYSER_VARIABLE_NAME.

        Returns:
          The CodeAanalyser instance to analyse the student's code with.

        """
        for name in ['ast', 'CodeAnalyser', 'TutorialNodeVisitor']:
            assert globals().get(name) is not None
        _, analysis_lcls = self.exec_submodule(
            Tutorial.ANALYSIS_MODULE, globals()
        )

        assert Tutorial.ANALYSIS_VARIABLE_NAME in analysis_lcls, \
            'Invalid .tut package: {} has no member {}'.format(
                Tutorial.ANALYSIS_MODULE, Tutorial.ANALYSIS_VARIABLE_NAME
            )

        return analysis_lcls[Tutorial.ANALYSIS_VARIABLE_NAME]

    @property
    def preload_code_text(self):
        """
        Return the code text to display to the user when this tutorial is
        first loaded.

        This property is implemented lazily.

        """
        if self._preload_code_text is None:
            self._preload_code_text = self.read_submodule(
                Tutorial.PRELOAD_MODULE
            )

        return self._preload_code_text
