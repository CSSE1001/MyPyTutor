class Person(object):
    def __init__(self, name, age, gender):
        """Constructor

        __init__(self, string, integer, char)"""

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
        return self._name

    def get_age(self):
        return self._age

    def get_gender(self):
        return self._gender

    def set_friend(self, friend):
        self._friend = friend

    def get_friend(self):
        return self._friend