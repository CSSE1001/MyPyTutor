class MeanReturnsAFloat(StudentTestCase):
    DESCRIPTION = 'mean returns a float'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return mean([1])

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, float)


class MeanOfSingleNumber(StudentTestCase):
    DESCRIPTION = 'mean([1]) -> 1.'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return mean([1])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1.)

    def test_alternate(self):
        def _get_results():
            return mean([2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 2.)


class MeanOfTwoNumbersIsWholeNumber(StudentTestCase):
    DESCRIPTION = 'mean([0, 2]) -> 1.'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return mean([0, 2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1.)

    def test_alternate(self):
        def _get_results():
            return mean([1, 3])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 2.)


class MeanOfTwoNumbersIsFraction(StudentTestCase):
    DESCRIPTION = 'mean([0, 1]) -> 0.5'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return mean([0, 1])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0.5)

    def test_alternate(self):
        def _get_results():
            return mean([1, 2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1.5)


class MeanOfFiveNumbers(StudentTestCase):
    DESCRIPTION = 'mean([2, 7, 3, 9, 13]) -> 6.8'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return mean([2, 7, 3, 9, 13])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 6.8)


TEST_CLASSES = [
    MeanOfSingleNumber,
    MeanOfTwoNumbersIsWholeNumber,
    MeanOfTwoNumbersIsFraction,
    MeanOfFiveNumbers,
]
