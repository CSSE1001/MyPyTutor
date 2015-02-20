class TestGetValue(StudentTestCase):
    DESCRIPTION = "get_value({'k': 3}, 'k') -> 3"
    MAIN_TEST = 'test_get_value'

    def test_get_value(self):
        def _get_results():
            value = get_value({'k': 3}, 'k')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, 3)

    def test_alternate(self):
        def _get_results():
            value = get_value({'j': 7}, 'j')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, 7)


class TestGetADifferentValue(StudentTestCase):
    DESCRIPTION = "get_value({'a': 1, 'b': 2, 'c': 3}, 'b') -> 2"
    MAIN_TEST = 'test_get_value'

    def test_get_value(self):
        def _get_results():
            value = get_value({'a': 1, 'b': 2, 'c': 3}, 'b')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, 2)

    def test_alternate(self):
        def _get_results():
            value = get_value({'d': 5, 'e': 21, 'f': 56}, 'e')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, 21)


class TestGetInvalidKey(StudentTestCase):
    DESCRIPTION = "get_value({'a': 1, 'b': 2, 'c': 3}, 'Not a key') -> -1"
    MAIN_TEST = 'test_get_value'

    def test_get_value(self):
        def _get_results():
            value = get_value({'a': 1, 'b': 2, 'c': 3}, 'Not a key')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, -1)

    def test_alternate(self):
        def _get_results():
            value = get_value({'Not a key': 'test12'}, 'Not a key')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, 'test12')


TEST_CLASSES = [
    TestGetValue,
    TestGetADifferentValue,
    TestGetInvalidKey,
]
