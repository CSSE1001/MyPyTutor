class TestGetValue(StudentTestCase):
    DESCRIPTION = "get_value({'k': 3}, 'k') -> 3"
    MAIN_TEST = 'test_get_value'

    def test_get_value(self):
        def _get_results():
            value = get_value({'k': 3}, 'k')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, 3)


class TestGetADifferentValue(StudentTestCase):
    DESCRIPTION = "get_value({'a': 1, 'b': 2, 'c': 3}, 'b') -> 2"
    MAIN_TEST = 'test_get_value'

    def test_get_value(self):
        def _get_results():
            value = get_value({'a': 1, 'b': 2, 'c': 3}, 'b')
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, 2)


TEST_CLASSES = [
    TestGetValue,
    TestGetADifferentValue,
]
