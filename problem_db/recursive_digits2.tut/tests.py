class RecursiveDigits2SingleBase10Digit(StudentTestCase):
    DESCRIPTION = 'dec2base(5, 10) -> [5]'
    MAIN_TEST = 'test_single_digit'

    def test_single_digit(self):
        result = self.run_student_code(5, 10)
        self.assertEqual(result, [5])

    def test_alternate(self):
        result = self.run_student_code(7, 10)
        self.assertEqual(result, [7])


class RecursiveDigits2SingleBase2Digit(StudentTestCase):
    DESCRIPTION = 'dec2base(1, 2) -> [1]'
    MAIN_TEST = 'test_single_digit'

    def test_single_digit(self):
        result = self.run_student_code(1, 2)
        self.assertEqual(result, [1])

    def test_alternate(self):
        result = self.run_student_code(0, 2)
        self.assertEqual(result, [0])


class RecursiveDigits2MultipleBase10Digits(StudentTestCase):
    DESCRIPTION = 'dec2base(120, 10) -> [1, 2, 0]'
    MAIN_TEST = 'test_multiple_digits'

    def test_multiple_digits(self):
        result = self.run_student_code(120, 10)
        self.assertEqual(result, [1, 2, 0])

    def test_alternate(self):
        result = self.run_student_code(57, 10)
        self.assertEqual(result, [5, 7])


class RecursiveDigits2MultipleBase8Digits(StudentTestCase):
    DESCRIPTION = 'dec2base(273, 8) -> [4, 2, 1]'
    MAIN_TEST = 'test_multiple_digits'

    def test_multiple_digits(self):
        result = self.run_student_code(273, 8)
        self.assertEqual(result, [4, 2, 1])

    def test_alternate(self):
        result = self.run_student_code(16, 8)
        self.assertEqual(result, [2, 0])


class RecursiveDigits2MultipleBase2Digits(StudentTestCase):
    DESCRIPTION = 'dec2base(61, 2) -> [1, 1, 1, 1, 0, 1]'
    MAIN_TEST = 'test_multiple_digits'

    def test_multiple_digits(self):
        result = self.run_student_code(61, 2)
        self.assertEqual(result, [1, 1, 1, 1, 0, 1])

    def test_alternate(self):
        result = self.run_student_code(7, 2)
        self.assertEqual(result, [1, 1, 1])


TEST_CLASSES = [
    RecursiveDigits2SingleBase10Digit,
    RecursiveDigits2SingleBase2Digit,
    RecursiveDigits2MultipleBase10Digits,
    RecursiveDigits2MultipleBase8Digits,
    RecursiveDigits2MultipleBase2Digits,
]
