class TestSingleDigit(StudentTestCase):
    DESCRIPTION = 'base2dec([1], 10) -> 1'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return base2dec([1], 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1)

    def test_alternate(self):
        def _get_results():
            return base2dec([5], 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 5)


class TestBaseTen(StudentTestCase):
    DESCRIPTION = 'base2dec([1, 2, 0], 10) -> 120'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return base2dec([1, 2, 0], 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 120)

    def test_alternate(self):
        def _get_results():
            return base2dec([5, 7], 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 57)


class TestBaseEight(StudentTestCase):
    DESCRIPTION = 'base2dec([4, 2, 1], 8) -> 273'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return base2dec([4, 2, 1], 8)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 273)

    def test_alternate(self):
        def _get_results():
            return base2dec([2, 0], 8)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 16)


class TestBaseTwo(StudentTestCase):
    DESCRIPTION = 'base2dec([1, 1, 1], 2) -> 7'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return base2dec([1, 1, 1], 2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 7)

    def test_alternate(self):
        def _get_results():
            return base2dec([1, 1, 1, 1, 0, 1], 2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 61)


TEST_CLASSES = [
    TestSingleDigit,
    TestBaseTen,
    TestBaseEight,
    TestBaseTwo,
]
