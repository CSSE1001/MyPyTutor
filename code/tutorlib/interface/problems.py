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
    CONFIG_FILE = 'tutorials.txt'

    def __init__(self, options):
        self.options = options
        path = os.path.join(options.tut_dir, TutorialPackage.CONFIG_FILE)

        try:
            with open(path) as f:
                self._parse_tutorial_config(f)
        except (FileNotFoundError, IOError) as e:
            ex = TutorialPackageError('Failed to parse tutorial config file')
            raise ex from e

    def __iter__(self):
        return iter(self.problem_sets)

    def _parse_tutorial_config(self, f):
        self.problem_sets = []
        problem_set = None

        for line in map(str.strip, f):
            if not line:
                continue

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
