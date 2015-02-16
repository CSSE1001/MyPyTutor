class TestAverage(StudentTestCase):
    DESCRIPTION = "'1.5', '2', '2.5', '' -> 2.0"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='1.5\n2\n2.5\n\n')
        self.assertEqual(self.standard_output, '2.0\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='1\n2\n3\n4\n\n')
        self.assertEqual(self.standard_output, '2.5\n')


class TestZero(StudentTestCase):
    DESCRIPTION = "'' > '0.0'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='\n')
        self.assertEqual(self.standard_output, '0.0\n')


TEST_CLASSES = [
    TestAverage,
    TestZero,
]
