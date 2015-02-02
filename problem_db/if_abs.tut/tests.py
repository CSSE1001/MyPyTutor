class TestPositiveNumber(StudentTestCase):
    DESCRIPTION = "'2' -> '2'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='2\n')
        self.assertEqual(self.standard_output, '2\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='5\n')
        self.assertEqual(self.standard_output, '5\n')


class TestNegativeNumber(StudentTestCase):
    DESCRIPTION = "'-2' -> '2'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='-2\n')
        self.assertEqual(self.standard_output, '2\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='-5\n')
        self.assertEqual(self.standard_output, '5\n')


class TestZero(StudentTestCase):
    DESCRIPTION = "'0' -> '0'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='0\n')
        self.assertEqual(self.standard_output, '0\n')


TEST_CLASSES = [
    TestPositiveNumber,
    TestNegativeNumber,
    TestZero,
]
