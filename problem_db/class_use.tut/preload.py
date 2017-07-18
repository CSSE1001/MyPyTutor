class Person(object):
    def __init__(self, name, age, gender):
        """Construct a person object given their name, age and gender

        Parameters:
            name(str): The name of the person
            age(int): The age of the person
            gender(str): Either 'M' or 'F' for male or female
        """

        self._name = name
        self._age = age
        self._gender = gender
        self._friend = None

    def __eq__(self, person):
        return str(self) == str(person)

    def __str__(self):
        if self._gender == 'M':
            title = 'Mr'
        elif self._gender == 'F':
            title = 'Miss'
        else:
            title = 'Ms'

        return title + ' ' + self._name + ' ' + str(self._age)

    def __repr__(self):
        return 'Person: ' + str(self)

    def get_name(self):
        """
        (str) Return the name
        """
        return self._name

    def get_age(self):
        """
        (int) Return the age
        """
        return self._age

    def get_gender(self):
        """
        (str) Return the gender
        """
        return self._gender

    def set_friend(self, friend):
        self._friend = friend

    def get_friend(self):
        """
        (Person) Return the friend
        """
        return self._friend
