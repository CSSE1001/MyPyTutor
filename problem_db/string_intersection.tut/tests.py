class TestNoIntersection(StudentTestCase):
    DESCRIPTION = "intersection('a', 'b') -> ''"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return intersection('a', 'b')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, '')

    def test_alternate(self):
        def _get_results():
            return intersection('c', 'd')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, '')


class TestSingleCharacterSame(StudentTestCase):
    DESCRIPTION = "intersection('a', 'a') -> 'a'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return intersection('a', 'a')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'a')

    def test_alternate(self):
        def _get_results():
            return intersection('c', 'c')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'c')


class TestTwoCharactersSame(StudentTestCase):
    DESCRIPTION = "intersection('aa', 'aa') -> 'a'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return intersection('aa', 'aa')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'a')

    def test_alternate(self):
        def _get_results():
            return intersection('cc', 'cc')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'c')


class TestTwoWords(StudentTestCase):
    DESCRIPTION = "intersection('monty', 'monty') -> 'monty'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return intersection('monty', 'monty')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'monty')

    def test_alternate(self):
        def _get_results():
            return intersection('clip', 'clip')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'clip')


class TestWordWithRepeatedCharacters(StudentTestCase):
    DESCRIPTION = "intersection('hello', 'hello') -> 'helo'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return intersection('hello', 'hello')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'helo')

    def test_alternate(self):
        def _get_results():
            return intersection('ccddee', 'ccddee')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'cde')


class TestDifferentWords(StudentTestCase):
    DESCRIPTION = "intersection('monty', 'python') -> 'onty'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return intersection('monty', 'python')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'onty')

    def test_alternate(self):
        def _get_results():
            return intersection('nope', 'yep')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'pe')


class TestSentences(StudentTestCase):
    DESCRIPTION = "intersection('On hot sunny days', 'There is much rain') -> 'n hsua'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return intersection('On hot sunny days', 'There is much rain')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'n hsua')


TEST_CLASSES = [
    TestNoIntersection,
    TestSingleCharacterSame,
    TestTwoCharactersSame,
    TestTwoWords,
    TestWordWithRepeatedCharacters,
    TestDifferentWords,
    TestSentences,
]
