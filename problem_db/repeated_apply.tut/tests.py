class TestSingleApply(StudentTestCase):
    DESCRIPTION = 'g = lambda x: x+1; repeatedlyApply(g, 1)(100) -> 101'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return repeatedlyApply(lambda x: x+1, 1)(100)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 101)

    def test_alternate(self):
        def _get_results():
            return repeatedlyApply(lambda x: 2*x, 1)(2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)


class TestMultipleApply(StudentTestCase):
    DESCRIPTION = 'g = lambda x: x+1; repeatedlyApply(g, 10)(100) -> 110'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return repeatedlyApply(lambda x: x+1, 10)(100)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 110)

    def test_alternate(self):
        def _get_results():
            return repeatedlyApply(lambda x: x*2, 4)(2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 32)




TEST_CLASSES = [
    TestSingleApply,
    TestMultipleApply,
]
