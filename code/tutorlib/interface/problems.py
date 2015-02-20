import os

from tutorlib.interface.tutorial import Tutorial


class TutorialPackageError(Exception):
    """
    An error encountered in loading a tutorial package.

    """
    pass


class ProblemSet():
    """
    A problem set (collection of tutorial problems due on the same date, or
    related in some other logical manner).

    Problem sets are iterable objects (and will iterate over their component
    problems).

    Attributes:
      name (str): The name of the problem set.
      date (str): The due date of the problem set.
      problems ([Tutorial]): The problems in the problem set.

    """
    def __init__(self, name, date):
        """
        Create a new ProblemSet object.

        Args:
          name (str): The name of the problem set.
          date (str): The due date of the problem set.

        """
        self.name = name
        self.date = date

        self.problems = []

    def __repr__(self):
        return 'ProblemSet({!r}, {!r})'.format(self.name, self.date)

    def __iter__(self):
        """
        Iterate over the problems in the problem set.

        Returns:
          An iterator over the problems in the problem set.

        """
        return iter(self.problems)

    def add_problem(self, tutorial):
        """
        Add a new tutorial problem to the problem set.

        Args:
          tutorial (Tutorial): The tutorial to add.

        """
        self.problems.append(tutorial)


class TutorialPackage():
    """
    A tutorial package (collection of problem sets).

    Class Attributes:
      TUTORIALS_FILE (constant): The filename of the configuration file
          containing details on problem sets.
      CONFIG_FILE (constant): The filename of the configuration file containing
          general configuration information on this tutorial package.

    Attributes:
      name (str): The name of the tutorial package.
      options (Namespace): Tutorial package options (as taken from the
          MyPytutor config data).  Contains `.tut_dir` and `.ans_dir`.

    """
    TUTORIALS_FILE = 'tutorials.txt'
    CONFIG_FILE = 'config.txt'

    def __init__(self, name, options):
        """
        Initialise a new TutorialPackage object.

        Args:
          name (str): The name of the tutorial package.
          options (Namespace): Tutorial package options (as taken from the
              MyPyTutor config data).

        Raises:
          TutorialPackageError: If any error is encountered while parsing the
             tutorial package, its component problem sets, or their component
             tutorial problems.

        """
        self.name = name
        self.options = options

        path = os.path.join(options.tut_dir, TutorialPackage.CONFIG_FILE)

        try:
            with open(path) as f:
                self._parse_config_file(f)
        except (FileNotFoundError, IOError) as e:
            ex = TutorialPackageError('Failed to parse tutorial config file')
            raise ex from e

        path = os.path.join(options.tut_dir, TutorialPackage.TUTORIALS_FILE)

        try:
            with open(path) as f:
                self._parse_tutorials_file(f)
        except (FileNotFoundError, IOError) as e:
            ex = TutorialPackageError('Failed to parse tutorials file')
            raise ex from e

    def _parse_config_file(self, f):
        """
        Parse the tutorial package configuration file.

        The expected format of the file has two lines.
        The first contains a timestamp.
        The second contains a url.

        The timestamp should not be converted to a float, as that could lose
        precision on the timestamp.

        Args:
          f (file): The tutorial package configuration file.

        Raises:
          TutorialPackageError: If the configuration file is not in the
              expected format.

        """
        # expected format
        # timestamp
        # url

        try:
            self.timestamp, self.url = filter(None, map(str.strip, f))
        except ValueError:
            raise TutorialPackageError(
                'Invalid configuration file (need timestamp and url)'
            )

    def _parse_tutorials_file(self, f):
        """
        Parse the problem set configuration file (list of tutorials).

        The file must have one or more section headers, of the format:
            [date section_name]

        followed by one or more problem descriptions, of the format:
            problem name:directory.tut

        Args:
          f (file): The problem set configuration file.

        Raises:
          TutorialPackageError: If the configuration file is not in the
              expected format, or if any of the tutorials do not exist.

        """
        self.problem_sets = []
        problem_set = None

        for line in filter(None, map(str.strip, f)):
            if line.startswith('['):
                try:
                    date, section = line.strip('[]').split(' ', 1)
                except ValueError:
                    raise TutorialPackageError(
                        'Invalid section header: {}'.format(line)
                    )

                problem_set = ProblemSet(section, date)
                self.problem_sets.append(problem_set)
            else:
                try:
                    name, directory = line.split(':')
                except ValueError:
                    raise TutorialPackageError(
                        'Invalid problem description: {}'.format(line)
                    )

                if problem_set is None:
                    raise TutorialPackageError(
                        'Encountered problem description before section header'
                    )

                tutorial_path = os.path.join(self.options.tut_dir, directory)
                answer_path = os.path.join(
                    self.options.ans_dir,
                    '{}.py'.format(name.replace(' ', '_'))
                )

                try:
                    tutorial = Tutorial(name, tutorial_path, answer_path)
                except AssertionError as e:
                    raise TutorialPackageError(
                        'Could not load tutorial with name: {}'.format(name)
                    ) from e

                problem_set.add_problem(tutorial)

    def _get_tutorial(self, current_tutorial, get_previous=True):
        """
        Get the next or previous tutorial after or before the given tutorial.

        Args:
          current_tutorial (Tutorial): The current tutorial (to base the next
              or previous tutorial decision off).
          get_previous (bool, optional): Whether to get the previous tutorial.
              Defaults to True.  If False, the next tutorial will be returned.

        Returns:
          The next or previous tutorial (as a Tutorial object).

          If the current tutorial is None, then the first tutorial will be
          returned.

          If the current tutorial is the first tutorial, and the previous
          tutorial is requested, then the first tutorial will be returned.

          If the current tutorial is the last tutorial, and the next tutorial
          is requested, then the last tutorial will be returned.

        """
        previous_tutorial = None
        return_next = current_tutorial is None  # return first if None

        for problem_set in self.problem_sets:
            for tutorial in problem_set:
                if return_next:
                    return tutorial
                elif tutorial == current_tutorial:
                    if get_previous:
                        return previous_tutorial or tutorial  # same if first
                    return_next = True
                previous_tutorial = tutorial

        return tutorial  # if at end, return same

    def next(self, current_tutorial):
        """
        Get the next tutorial after the given tutorial.

        Args:
          current_tutorial (Tutorial): The current tutorial.

        Returns:
          The next tutorial (as a Tutorial object).

          If the current tutorial is None, then the first tutorial will be
          returned.

          If the current tutorial is the last tutorial, then this method will
          return the last (current) tutorial.

        """
        return self._get_tutorial(current_tutorial, get_previous=False)

    def previous(self, current_tutorial):
        """
        Get the previous tutorial before the given tutorial.

        Args:
          current_tutorial (Tutorial): The current tutorial.

        Returns:
          The next tutorial (as a Tutorial object).

          If the current tutorial is None, then the first tutorial will be
          returned.

          If the current tutorial is the first tutorial, then this method
          will return the first (current) tutorial.

        """
        return self._get_tutorial(current_tutorial, get_previous=True)

    def tutorial_with_name(self, tutorial_name):
        """
        Return the tutorial with the given name.

        Args:
          tutorial_name (str): The name of the tutorial to return.

        Returns:
          The tutorial with the name `tutorial_name`.

          If no such tutorial exists, return None.

          If multiple tutorials with the given name exist, the first (with the
          earliest appearance in the earliest problem set) will be returned.

        """
        for problem_set in self.problem_sets:
            for tutorial in problem_set:
                if tutorial.name == tutorial_name:
                    return tutorial
        return None

    def tutorial_with_hash(self, tutorial_hash):
        """
        Return the tutorial with the given hash.

        Args:
          tutorial_hash (str): The hash of the tutorial to return.

        Returns:
          The tutorial with the given hash.

          If no such tutorial exists, return None.

          If multiple tutorials with the given hash exist, the first (with the
          earliest appearance in the earliest problem set) will be returned.

        """
        for problem_set in self.problem_sets:
            for tutorial in problem_set:
                if tutorial.hash == tutorial_hash:
                    return tutorial
        return None

    def problem_set_containing(self, tutorial):
        """
        Return the problem set containing the given tutorial.

        Args:
          tutorial (Tutorial): The tutorial to search for.

        Returns:
          The problem set containing the tutorial, if one exists.
          None otherwise.

        """
        for problem_set in self.problem_sets:
            for ps_tutorial in problem_set:
                if ps_tutorial == tutorial:
                    return problem_set

        return None
