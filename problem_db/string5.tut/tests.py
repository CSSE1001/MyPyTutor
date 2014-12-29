class TestResultIsAString(StudentTestCase):
    DESCRIPTION = 'get_digits returns a string'
    MAIN_TEST = 'test_result_is_string'

    def test_result_is_string(self):
        def _get_results():
            return get_digits('1234')

        digits = self.run_in_student_context(_get_results)
        self.assertIsInstance(digits, str)


class TestDigitOnlyString(StudentTestCase):
    DESCRIPTION = "get_digits('1234') -> '1234'"
    MAIN_TEST = 'test_digits_only'

    def test_digits_only(self):
        def _get_results():
            return get_digits('1234')

        digits = self.run_in_student_context(_get_results)
        self.assertEqual(digits, '1234')

    def test_alternate(self):
        def _get_results():
            return get_digits('088')

        digits = self.run_in_student_context(_get_results)
        self.assertEqual(digits, '088')


class TestWithBreakInMiddle(StudentTestCase):
    DESCRIPTION = "get_digits('12_34') -> '1234'"
    MAIN_TEST = 'test_with_break'

    def test_with_break(self):
        def _get_results():
            return get_digits('12_34')

        digits = self.run_in_student_context(_get_results)
        self.assertEqual(digits, '1234')

    def test_alternate(self):
        def _get_results():
            return get_digits('99+100=199')

        digits = self.run_in_student_context(_get_results)
        self.assertEqual(digits, '99100199')


class TestWithNonDigitsOnEnds(StudentTestCase):
    DESCRIPTION = "get_digits('n12+34b') -> '1234'"
    MAIN_TEST = 'test_with_non_digits_on_ends'

    def test_with_non_digits_on_ends(self):
        def _get_results():
            return get_digits('n12+34b')

        digits = self.run_in_student_context(_get_results)
        self.assertEqual(digits, '1234')

    def test_alternate(self):
        def _get_results():
            return get_digits('kkkk8kkkk')

        digits = self.run_in_student_context(_get_results)
        self.assertEqual(digits, '8')


class TestEmptyString(StudentTestCase):
    DESCRIPTION = "get_digits('') -> ''"
    MAIN_TEST = 'test_empty_string'

    def test_empty_string(self):
        def _get_results():
            return get_digits('')

        digits = self.run_in_student_context(_get_results)
        self.assertEqual(digits, '')


TEST_CLASSES = [
    TestResultIsAString,
    TestDigitOnlyString,
    TestWithBreakInMiddle,
    TestWithNonDigitsOnEnds,
    TestEmptyString,
]
