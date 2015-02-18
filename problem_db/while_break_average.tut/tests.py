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


class TestSingle(StudentTestCase):
    DESCRIPTION = "'3.3', '' > '3.3'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='3.3\n\n')
        self.assertEqual(self.standard_output, '3.3\n')


TEST_CLASSES = [
    TestAverage,
    TestSingle,
]
