class TestNegative(StudentTestCase):
    DESCRIPTION = "'-6' -> 'negative'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='-6\n')
        self.assertEqual(self.standard_output, 'negative\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='-1\n')
        self.assertEqual(self.standard_output, 'negative\n')


class TestZero(StudentTestCase):
    DESCRIPTION = "'0' -> 'zero'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='0\n')
        self.assertEqual(self.standard_output, 'zero\n')

class TestPositive(StudentTestCase):
    DESCRIPTION = "'4' -> 'positive'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='4\n')
        self.assertEqual(self.standard_output, 'positive\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='1\n')
        self.assertEqual(self.standard_output, 'positive\n')



TEST_CLASSES = [
    TestNegative,
    TestZero,
    TestPositive
]
