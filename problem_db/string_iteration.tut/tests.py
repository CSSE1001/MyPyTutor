class TestSingleCharacterFirstArgument(StudentTestCase):
    DESCRIPTION = "occurrences('a', 'aaa') -> 3"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return occurrences('a', 'aaa')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 3)

    def test_alternate(self):
        def _get_results():
            return occurrences('b', 'bbbbb')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 5)


class TestSingleCharacterSecondArgument(StudentTestCase):
    DESCRIPTION = "occurrences('aaa', 'a') -> 1"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return occurrences('aaa', 'a')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1)

    def test_alternate(self):
        def _get_results():
            return occurrences('bbbbb', 'b')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1)


class TestIdenticalArguments(StudentTestCase):
    DESCRIPTION = "occurrences('Hello', 'Hello') -> 5"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return occurrences('Hello', 'Hello')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 5)

    def test_alternate(self):
        def _get_results():
            return occurrences('Goodbye', 'Goodbye')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 7)


class TestFooled(StudentTestCase):
    DESCRIPTION = "occurrences('fooled', 'hello world') -> 7"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return occurrences('fooled', 'hello world')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 7)

    def test_alternate(self):
        def _get_results():
            return occurrences('monty', 'python')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)


TEST_CLASSES = [
    TestSingleCharacterFirstArgument,
    TestSingleCharacterSecondArgument,
    TestIdenticalArguments,
    TestFooled,
]
