class HelloTests(StudentTestCase):
    DESCRIPTION = "prints 'Hello, World!'"
    MAIN_TEST = 'test_hello'

    def test_hello(self):
        def _get_results():
            _function_under_test()
        self.run_in_student_context(_get_results)
        expected = 'Hello, World!\n'
        self.assertEqual(self.standard_output, expected)


TEST_CLASSES = [
    HelloTests,
]
