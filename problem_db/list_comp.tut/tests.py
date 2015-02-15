class TestWithEmpty(StudentTestCase):
    DESCRIPTION = 'square_odds([]) -> []'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square_odds([]) 

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [])


class TestWithMix(StudentTestCase):
    DESCRIPTION = 'square_odds([1,2,3,4,5]) -> [1,9,25]'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square_odds([1,2,3,4,5])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [1,9,25])

    def test_alternate(self):
        def _get_results():
            return square_odds([5,7,2,1,4,6])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [25,49,1])


class TestWithOnlyOdds(StudentTestCase):
    DESCRIPTION = 'square_odds([7,3,5]) -> [49,9,25]'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square_odds([7,3,5])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [49,9,25])

    def test_alternate(self):
        def _get_results():
            return square_odds([7,1,9])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [49,1,81])

class TestWithOnlyEvens(StudentTestCase):
    DESCRIPTION = 'square_odds([2,4,8]) -> []'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square_odds([2, 4, 8])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [])

    def test_alternate(self):
        def _get_results():
            return square_odds([2,2,6])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [])




TEST_CLASSES = [
    TestWithEmpty,
    TestWithMix,
    TestWithOnlyOdds,
    TestWithOnlyEvens
]
