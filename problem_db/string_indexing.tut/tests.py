class TestSpam(StudentTestCase):
    DESCRIPTION = "'Spam' -> 'S', 'p', 'm'"
    MAIN_TEST = 'test_spam'

    def test_spam(self):
        def _get_results():
            _function_under_test()

        # we just need the output
        _ = self.run_in_student_context(_get_results, input_text='Spam')

        # check that the output matches
        expected_output = 'S\np\nm\n'
        self.assertEqual(self.standard_output, expected_output)

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results, input_text='abcd')

        expected_output = 'a\nb\nd\n'
        self.assertEqual(self.standard_output, expected_output)


class TestPython(StudentTestCase):
    DESCRIPTION = "'Python' -> 'P', 'y', 'n'"
    MAIN_TEST = 'test_python'

    def test_python(self):
        def _get_results():
            _function_under_test()

        # we just need the output
        _ = self.run_in_student_context(_get_results, input_text='Python')

        # check that the output matches
        expected_output = 'P\ny\nn\n'
        self.assertEqual(self.standard_output, expected_output)

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results, input_text='thingy')

        expected_output = 't\nh\ny\n'
        self.assertEqual(self.standard_output, expected_output)


class TestNo(StudentTestCase):
    DESCRIPTION = "'No' -> 'N', 'o', 'o'"
    MAIN_TEST = 'test_no'

    def test_no(self):
        def _get_results():
            _function_under_test()

        # we just need the output
        _ = self.run_in_student_context(_get_results, input_text='No')

        # check that the output matches
        expected_output = 'N\no\no\n'
        self.assertEqual(self.standard_output, expected_output)

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results, input_text='hi')

        expected_output = 'h\ni\ni\n'
        self.assertEqual(self.standard_output, expected_output)


TEST_CLASSES = [
    TestSpam,
    TestPython,
    TestNo,
]
