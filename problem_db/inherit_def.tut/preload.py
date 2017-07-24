class Employee(object):
    """
    A salaried employee.

    """
    def __init__(self, name, salary):
        """
        Initialise a new Employee instance.

        Parameters:
            name (str): The employee's name.
            salary (float): The employee's annual salary.

        """
        self._name = name
        self._salary = salary

    def get_name(self):
        """
        (str) Return the name.

        """
        return self._name

    def wage(self):
        """
        (float) Return the forgnightly wage.

        """
        return self._salary/26
