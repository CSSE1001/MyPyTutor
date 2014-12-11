class Fun1Tests(StudentTestCase):
    DESCRIPTION = 'output 2*(n + 1)'
    MAIN_TEST = 'test_fun1'

    def test_fun1(self):
        # we don't care about the result here - just the output
        _ = self.run_student_code(input_text='2')

        # check that they printed the output correctly
        expected_output = '6\n'  # 2*(2 + 1)
        self.assertEqual(self.standard_output, expected_output)

    def test_fun1_hidden(self):
        _ = self.run_student_code(input_text='0')

        expected_output = '2\n'  # 2*(0 + 1)
        self.assertEqual(self.standard_output, expected_output)


TEST_CLASSES = [
    Fun1Tests,
]