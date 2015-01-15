class TestSumEmptyRange(StudentTestCase):
    DESCRIPTION = 'sum_range(0, 0) -> 0'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_range(0, 0)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)

    def test_alternate(self):
        def _get_results():
            return sum_range(1, 1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)


class TestSumEmptyRangeWithLowerSecondBound(StudentTestCase):
    DESCRIPTION = 'sum_range(5, 0) -> 0'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_range(5, 0)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)

    def test_alternate(self):
        def _get_results():
            return sum_range(8, 1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)


class TestSumSimpleRange(StudentTestCase):
    DESCRIPTION = 'sum_range(10, 12) -> 21'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_range(10, 12)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 21)

    def test_alternate(self):
        def _get_results():
            return sum_range(50, 52)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 101)


class TestSumEvensEmptyRange(StudentTestCase):
    DESCRIPTION = 'sum_evens(0, 0) -> 0'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_evens(0, 0)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)

    def test_alternate(self):
        def _get_results():
            return sum_evens(50, 50)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)


class TestSumEvensEmptyRangeWithLowerSecondBound(StudentTestCase):
    DESCRIPTION = 'sum_evens(5, 0) -> 0'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_evens(5, 0)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)

    def test_alternate(self):
        def _get_results():
            return sum_evens(50, 10)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)


class TestSumEvensFirstNumberEven(StudentTestCase):
    DESCRIPTION = 'sum_evens(2, 5) -> 6'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_evens(2, 5)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 6)

    def test_alternate(self):
        def _get_results():
            return sum_evens(8, 11)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 18)


class TestSumEvensFirstNumberOdd(StudentTestCase):
    DESCRIPTION = 'sum_evens(1, 5) -> 6'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_evens(1, 5)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 6)

    def test_alternate(self):
        def _get_results():
            return sum_evens(7, 11)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 18)


TEST_CLASSES = [
    TestSumEmptyRange,
    TestSumEmptyRangeWithLowerSecondBound,
    TestSumSimpleRange,
    TestSumEvensEmptyRange,
    TestSumEvensEmptyRangeWithLowerSecondBound,
    TestSumEvensFirstNumberEven,
    TestSumEvensFirstNumberOdd,
]
