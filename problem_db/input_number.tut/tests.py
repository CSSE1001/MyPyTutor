class TestZeroHours(StudentTestCase):
    DESCRIPTION = "'0' -> '0'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='0\n')
        self.assertEqual(self.standard_output, '0\n')


class TestTwoHours(StudentTestCase):
    DESCRIPTION = "'2' -> '120'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='2\n')
        self.assertEqual(self.standard_output, '120\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='5\n')
        self.assertEqual(self.standard_output, '300\n')


TEST_CLASSES = [
    TestZeroHours,
    TestTwoHours,
]
