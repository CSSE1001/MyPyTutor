class TestVowel(StudentTestCase):
    DESCRIPTION = "'a' -> 'vowel'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='a\n')
        self.assertEqual(self.standard_output, 'vowel\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='e\n')
        self.assertEqual(self.standard_output, 'vowel\n')


class TestConsonant(StudentTestCase):
    DESCRIPTION = "'b' -> 'consonant'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='b\n')
        self.assertEqual(self.standard_output, 'consonant\n')

    def test_alternate(self):
        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text='g\n')
        self.assertEqual(self.standard_output, 'consonant\n')


TEST_CLASSES = [
    TestVowel,
    TestConsonant,
]
