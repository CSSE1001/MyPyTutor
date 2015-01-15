class Employee(object):
    """
    A salaried employee.

    """
    def __init__(self, name, salary):
        """
        Initialise a new Employee instance.

        Args:
          name (str): The employee's name.
          salary (float): The employee's annual salary.

        """
        self._name = name
        self._salary = salary

    def get_name(self):
        """
        Return the name of this employee.

        """
        return self._name

    def wage(self):
        """
        Return the forgnightly wage of this employee.

        """
        return self._salary/26