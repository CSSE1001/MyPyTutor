class TestPositiveNumber(StudentTestCase):
    DESCRIPTION = "'2' -> '6'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        # we don't care about the result here - just the output
        _ = self.run_in_student_context(_get_results, input_text='2\n')

        # check that they printed the output correctly
        expected_output = '6\n'  # 2*(2 + 1)
        self.assertEqual(self.standard_output, expected_output)

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results, input_text='3\n')

        expected_output = '8\n'  # 2*(3 + 1)
        self.assertEqual(self.standard_output, expected_output)


class TestZeroNumber(StudentTestCase):
    DESCRIPTION = "'0' -> '2'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results, input_text='0\n')

        expected_output = '2\n'  # 2*(0 + 1)
        self.assertEqual(self.standard_output, expected_output)


class TestNegativeNumber(StudentTestCase):
    DESCRIPTION = "'-3' -> '-4'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results, input_text='-3\n')

        expected_output = '-4\n'  # 2*(-3 + 1)
        self.assertEqual(self.standard_output, expected_output)

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results, input_text='-1\n')

        expected_output = '0\n'  # 2*(-1 + 1)
        self.assertEqual(self.standard_output, expected_output)


TEST_CLASSES = [
    TestPositiveNumber,
    TestZeroNumber,
    TestNegativeNumber,
]
