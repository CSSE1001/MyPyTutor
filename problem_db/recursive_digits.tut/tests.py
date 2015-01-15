class TestSingleDigit(StudentTestCase):
    DESCRIPTION = 'getdigits(5) -> [5]'
    MAIN_TEST = 'test_single_digit'

    def test_single_digit(self):
        def _get_results():
            return getdigits(5)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [5])

    def test_alternate(self):
        def _get_results():
            return getdigits(7)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [7])


class TestMultipleDigits(StudentTestCase):
    DESCRIPTION = 'getdigits(120) -> [1, 2, 0]'
    MAIN_TEST = 'test_multiple_digits'

    def test_multiple_digits(self):
        def _get_results():
            return getdigits(120)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [1, 2, 0])

    def test_alternate(self):
        def _get_results():
            return getdigits(57)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [5, 7])


TEST_CLASSES = [
    TestSingleDigit,
    TestMultipleDigits,
]
