class TestBasicName(StudentTestCase):
    DESCRIPTION = "get_names() < 'John Smith' -> ('John', 'Smith')"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return get_names()

        result = self.run_in_student_context(
            _get_results, input_text='John Smith'
        )
        self.assertEqual(result, ('John', 'Smith'))

    def test_alternate(self):
        def _get_results():
            return get_names()

        result = self.run_in_student_context(
            _get_results, input_text='Bob Bloggs'
        )
        self.assertEqual(result, ('Bob', 'Bloggs'))


class TestTwoLastNames(StudentTestCase):
    DESCRIPTION = "get_names() < 'John Albert Smith' -> ('John', 'Albert Smith')"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return get_names()

        result = self.run_in_student_context(
            _get_results, input_text='John Albert Smith'
        )
        self.assertEqual(result, ('John', 'Albert Smith'))

    def test_alternate(self):
        def _get_results():
            return get_names()

        result = self.run_in_student_context(
            _get_results, input_text='Bob Mary Bloggs'
        )
        self.assertEqual(result, ('Bob', 'Mary Bloggs'))


TEST_CLASSES = [
    TestBasicName,
    TestTwoLastNames,
]
