class TestWithSingleFunctionUnity(StudentTestCase):
    DESCRIPTION = 'f = lambda x: x; g = add_functions(f, f); g(2) -> 4'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return add_functions(lambda x: x, lambda x: x)(2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)

    def test_alternate(self):
        def _get_results():
            return add_functions(lambda x: x, lambda x: x)(1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 2)


class TestWithTwoFunctions(StudentTestCase):
    DESCRIPTION = 'g = add_functions(lambda x: x*2, lambda x: x + 1); g(2) -> 7'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return add_functions(lambda x: x*2, lambda x: x + 1)(2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 7)

    def test_alternate(self):
        def _get_results():
            return add_functions(lambda x: x*2, lambda x: x + 1)(1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)


class TestWithTwoOtherFunctions(StudentTestCase):
    DESCRIPTION = 'g = add_functions(lambda x: x - 2, lambda x: x**3); g(2) -> 8'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return add_functions(lambda x: x - 2, lambda x: x**3)(2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 8)

    def test_alternate(self):
        def _get_results():
            return add_functions(lambda x: x - 2, lambda x: x**3)(1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)


TEST_CLASSES = [
    TestWithSingleFunctionUnity,
    TestWithTwoFunctions,
    TestWithTwoOtherFunctions,
]
