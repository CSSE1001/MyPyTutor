import json
import os

from tutorlib.config.shared import TUTORIAL_ATTEMPTS_FILE


class TutorialAttempts():
    """
    A representation of the number of attempts a student has made at various
    tutorial problems.

    Attributes:
      attempts ({str: {str: {str: int}}}): The student's attempts at the
        tutorial problems.
      path (str): The path to the tutorial attempts file to use.

    """
    def __init__(self, path=TUTORIAL_ATTEMPTS_FILE):
        self.path = path

        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write(json.dumps({}))

        with open(self.path) as f:
            self.attempts = json.loads(f.read())

    def save(self):
        """
        Save the student's attempts.

        """
        with open(self.path, 'w') as f:
            f.write(json.dumps(self.attempts))

    def record_attempt(self, tutorial, tutorial_package):
        """
        Record an attempt for the student at the given tutorial in the given
        attempts dictionary.

        Args:
          tutorial (Tutorial): The tutorial to record the attempt for.
          tutorial_package (TutorialPackage): The tutorial package that the
            given tutorial belongs to.

        """
        if tutorial_package.name not in self.attempts:
            self.attempts[tutorial_package.name] = {}
        package_attempts = self.attempts[tutorial_package.name]

        problem_set = tutorial_package.problem_set_containing(tutorial)
        assert problem_set is not None, \
                'Tutorial {} not found on package {}'.format(
                    tutorial, tutorial_package
                )

        if problem_set.name not in package_attempts:
            package_attempts[problem_set.name] = {}
        pset_attempts = package_attempts[problem_set.name]

        if tutorial.name not in pset_attempts:
            pset_attempts[tutorial.name] = 0
        pset_attempts[tutorial.name] += 1

    def num_attempts_for(self, tutorial, tutorial_package):
        """
        Return the number of attempts for the given tutorial.

        Args:
          tutorial (Tutorial): The tutorial to return the current number of
            attempts for.
          tutorial_package (TutorialPackage): The tutorial package that the
            given tutorial belongs to.

        Returns:
          The number of attempts for the given tutorial.

        """
        problem_set = tutorial_package.problem_set_containing(tutorial)
        assert problem_set is not None, \
            'Tutorial {} not found on package {}'.format(
                tutorial, tutorial_package
            )

        return self.attempts.get(tutorial_package.name, {})\
                .get(problem_set.name, {}).get(tutorial.name, 0)
