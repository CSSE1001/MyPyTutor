import os

from tutorlib.interface.tutorial import Tutorial


class TutorialPackageError(Exception):
    pass


class ProblemSet():
    def __init__(self, name, date):
        self.name = name
        self.date = date

        self.problems = []

    def __repr__(self):
        return 'ProblemSet({!r}, {!r})'.format(self.name, self.date)

    def __iter__(self):
        return iter(self.problems)

    def add_problem(self, tutorial):
        self.problems.append(tutorial)


class TutorialPackage():
    TUTORIALS_FILE = 'tutorials.txt'
    CONFIG_FILE = 'config.txt'

    def __init__(self, options):
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
        # expected format
        # timestamp
        # url

        try:
            timestamp, self.url = filter(None, map(str.strip, f))
        except ValueError:
            raise TutorialPackageError(
                'Invalid configuration file (need timestamp and url)'
            )

        self.timestamp = float(timestamp)

    def _parse_tutorials_file(self, f):
        # expected file format:
        # [date section_name]
        # problem_name:problem_directory
        # ...

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

                path = os.path.join(self.options.tut_dir, directory)
                try:
                    tutorial = Tutorial(name, path)
                except AssertionError as e:
                    # TODO: in testing, ignore this
                    # TODO: in production, remove the continue
                    continue
                    ex = TutorialPackageError(
                        'Could not load tutorial at path: {}'.format(path)
                    )
                    raise ex from e

                problem_set.add_problem(tutorial)

    def _get_tutorial(self, current_tutorial, get_previous=True):
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
        return self._get_tutorial(current_tutorial, get_previous=False)

    def previous(self, current_tutorial):
        return self._get_tutorial(current_tutorial, get_previous=True)
