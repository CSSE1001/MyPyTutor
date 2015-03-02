class TestSquarePositive(StudentTestCase):
    DESCRIPTION = "square(3) -> 9"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square(3)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 9)

    def test_alternate(self):
        def _get_results():
            return square(7)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 49)


class TestSquareNegative(StudentTestCase):
    DESCRIPTION = "square(-2) -> 4"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square(-2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)

    def test_alternate(self):
        def _get_results():
            return square(-7)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 49)


class TestSquareZero(StudentTestCase):
    DESCRIPTION = "square(0) -> 0"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square(0)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)


TEST_CLASSES = [
    TestSquarePositive,
    TestSquareNegative,
    TestSquareZero,
]
