from abc import ABCMeta, abstractmethod
import ast


class ListGeneratingNodeVisitor(ast.NodeVisitor):
    """
    A NodeVisitor subclass which logs the order in which nodes are visited.

    This makes use of the default implementation of NodeVisitor.generic_visit,
    which recursively visits children of nodes.

    Attributes:
      VISIT (constant): Identifier for the start of a node visit.  This is
          appended to the events list immediately before a node is visited.
      LEAVE (constant): Identifier for thee end of a node visit.  This is
          appended to the events list immediately after a node is visited (and
          so also after all of its children have been visited).

      events ([constant, ast.AST]): List of visitation events.  The first item
          in each pair will be one of VISIT or LEAVE, as appropriate.  The
          second item in each pair is the node in question.

    """
    VISIT = 'VISIT'
    LEAVE = 'LEAVE'

    def __init__(self):
        self.events = []

    def generic_visit(self, node):
        self.events.append((ListGeneratingNodeVisitor.VISIT, node))
        super().generic_visit(node)
        self.events.append((ListGeneratingNodeVisitor.LEAVE, node))


class CodeAnalyser(metaclass=ABCMeta):
    """
    Abstract base class for analysis of student code.

    This class must not be instantiated.  Subclasses must override ._analyse

    Provides basic logic for analysing student code using a subclass of
    ast.NodeVisitor, as well as for recording the errors and warnings that may
    be generated in the analysis.

    Attributes:
      visitor (ast.NodeVisitor): The code visitor used in the analysis.
      errors ([str]): The error messages logged by the CodeAnalyser subclass,
          in the order encountered.
      warnings ([str]): The warning messages logged by the CodeAnalyser
          subclass, in the order encountered.

    """
    def __init__(self, visitor_class):
        """
        Initialise a new CodeAnalyser object.

        Args:
          visitor_class (ast.NodeVisitor class): The type of NodeVisitor to use
            when analysing the student code.  Note that this argument must be
            a class object, *not an instance of that class*.

        """
        self.visitor = visitor_class()

        self.errors = []
        self.warnings = []

    def add_error(self, message):
        """
        Add the given error message to the list of errors.

        Args:
            message (str): The error message to add.

        """
        self.errors.append(message)

    def add_warning(self, message):
        """
        Add the given warning message to the list of warnings.

        Args:
            message (str): The warning message to add.

        """
        self.warnings.append(message)

    def analyse(self, text):
        """
        Analyse the given student code text.

        Analysis will be performed using the visitor class given as an argument
        to the constructor.  This method ensures that all nodes are visited in
        the appropriate order, but does not attempt to log any errors or
        warnings that may be encountered.

        Defers to ._analyse() for detailed, problem-specific analysis.

        Args:
          text (str): The code to analyse.

        """
        # build up an ordered list of nodes in the default manner
        tree = ast.parse(text)

        list_generating_visitor = ListGeneratingNodeVisitor()
        list_generating_visitor.visit(tree)

        # visit each node in turn with our visitor (which will not recurse)
        handle_event = {
            ListGeneratingNodeVisitor.VISIT: self.visitor.visit,
            ListGeneratingNodeVisitor.LEAVE: self.visitor.leave,
        }
        for event, node in list_generating_visitor.events:
            assert event in handle_event, 'Unknown event: {}'.format(event)
            handle_event[event](node)

        # defer detailed analysis to subclasses
        self._analyse()

    @abstractmethod
    def _analyse(self):
        """
        Analyse the given student code text.

        This method performs detailed, problem-specific analysis on the student
        code.  It must be overriden by subclasses.

        Subclasses should make use of the visitor attribute (self.visitor) in
        order to identify errors and warnings, then add them through calls to
        .add_error() and .add_warning() respectively.

        """
        pass

    def check_for_errors(self, text):
        """
        Check whether the given student code has any compile errors.

        This method is only designed to detect compile errors which can be
        highlighted in the GUI.  If an exception is raised during compilation
        which does not have an associated line number, it will be ignored.

        Those exceptions will be dealt with during the testing phase.

        Args:
          text (str): The code to analyse.

        Returns:
          The line number associated with exception, if any.

          None if no exception was raised, or if an exception with no
          associated line number was encountered.

        """
        try:
            compile(text, '<student_code>', 'exec')
        except Exception as e:
            message = '{}: {}'.format(type(e).__name__, e)
            self.add_error(message)
            return getattr(e, 'lineno', None)

        return None
