class TestFullSlice(StudentTestCase):
    DESCRIPTION = "s = 'Hello'; slice_from(s, 0, len(s)) -> 'Hello'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            s = 'Hello'
            return slice_from(s, 0, len(s))

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Hello')

    def test_alternate(self):
        def _get_results():
            s = 'Goodbye'
            return slice_from(s, 0, len(s))

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Goodbye')


class TestClippingFirstAndLast(StudentTestCase):
    DESCRIPTION = "s = 'Hello'; slice_from(s, 1, len(s) - 1) -> 'ell'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            s = 'Hello'
            return slice_from(s, 1, len(s) - 1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'ell')

    def test_alternate(self):
        def _get_results():
            s = 'Goodbye'
            return slice_from(s, 1, len(s) - 1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'oodby')


class TestSliceFromThirdCharacterOnwards(StudentTestCase):
    DESCRIPTION = "s = 'Hello'; slice_from(s, 2, len(s)) -> 'llo'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            s = 'Hello'
            return slice_from(s, 2, len(s))

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'llo')

    def test_alternate(self):
        def _get_results():
            s = 'Goodbye'
            return slice_from(s, 2, len(s))

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'odbye')


class TestReverseSingleCharacter(StudentTestCase):
    DESCRIPTION = "reverse_string('a') -> 'a'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return reverse_string('a')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'a')

    def test_alternate(self):
        def _get_results():
            return reverse_string('z')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'z')


class TestReverseTwoCharacters(StudentTestCase):
    DESCRIPTION = "reverse_string('ab') -> 'ba'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return reverse_string('ab')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'ba')

    def test_alternate(self):
        def _get_results():
            return reverse_string('zy')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'yz')


class TestReverseHello(StudentTestCase):
    DESCRIPTION = "reverse_string('Hello') -> 'olleH'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return reverse_string('Hello')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'olleH')

    def test_alternate(self):
        def _get_results():
            return reverse_string('Goodbye')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'eybdooG')


TEST_CLASSES = [
    TestFullSlice,
    TestClippingFirstAndLast,
    TestSliceFromThirdCharacterOnwards,
    TestReverseSingleCharacter,
    TestReverseTwoCharacters,
    TestReverseHello,
]
