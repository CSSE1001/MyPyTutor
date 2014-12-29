class RecursiveDigits2SingleBase10Digit(StudentTestCase):
    DESCRIPTION = 'dec2base(5, 10) -> [5]'
    MAIN_TEST = 'test_single_digit'

    def test_single_digit(self):
        def _get_results():
            return dec2base(5, 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [5])

    def test_alternate(self):
        def _get_results():
            return dec2base(7, 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [7])


class RecursiveDigits2SingleBase2Digit(StudentTestCase):
    DESCRIPTION = 'dec2base(1, 2) -> [1]'
    MAIN_TEST = 'test_single_digit'

    def test_single_digit(self):
        def _get_results():
            return dec2base(1, 2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [1])

    def test_alternate(self):
        def _get_results():
            return dec2base(0, 2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [0])


class RecursiveDigits2MultipleBase10Digits(StudentTestCase):
    DESCRIPTION = 'dec2base(120, 10) -> [1, 2, 0]'
    MAIN_TEST = 'test_multiple_digits'

    def test_multiple_digits(self):
        def _get_results():
            return dec2base(120, 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [1, 2, 0])

    def test_alternate(self):
        def _get_results():
            return dec2base(57, 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [5, 7])


class RecursiveDigits2MultipleBase8Digits(StudentTestCase):
    DESCRIPTION = 'dec2base(273, 8) -> [4, 2, 1]'
    MAIN_TEST = 'test_multiple_digits'

    def test_multiple_digits(self):
        def _get_results():
            return dec2base(273, 8)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [4, 2, 1])

    def test_alternate(self):
        def _get_results():
            return dec2base(16, 8)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [2, 0])


class RecursiveDigits2MultipleBase2Digits(StudentTestCase):
    DESCRIPTION = 'dec2base(61, 2) -> [1, 1, 1, 1, 0, 1]'
    MAIN_TEST = 'test_multiple_digits'

    def test_multiple_digits(self):
        def _get_results():
            return dec2base(61, 2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [1, 1, 1, 1, 0, 1])

    def test_alternate(self):
        def _get_results():
            return dec2base(7, 2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [1, 1, 1])


TEST_CLASSES = [
    RecursiveDigits2SingleBase10Digit,
    RecursiveDigits2SingleBase2Digit,
    RecursiveDigits2MultipleBase10Digits,
    RecursiveDigits2MultipleBase8Digits,
    RecursiveDigits2MultipleBase2Digits,
]
