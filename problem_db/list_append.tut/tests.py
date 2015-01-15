class TestSingleString(StudentTestCase):
    DESCRIPTION = "add_sizes(['hello']) -> [('hello', 5)]"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return add_sizes(['hello'])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [('hello', 5)])

    def test_alternate(self):
        def _get_results():
            return add_sizes(['bye'])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [('bye', 3)])


class TestTwoStrings(StudentTestCase):
    DESCRIPTION = "add_sizes(['hello', 'world']) -> [('hello', 5), ('world', 5)]"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return add_sizes(['hello', 'world'])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [('hello', 5), ('world', 5)])

    def test_alternate(self):
        def _get_results():
            return add_sizes(['bye', 'you'])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [('bye', 3), ('you', 3)])


class TestEmptyList(StudentTestCase):
    DESCRIPTION = "add_sizes([]) -> []"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return add_sizes([])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [])


class TestDoesNotModifyInput(StudentTestCase):
    DESCRIPTION = 'does not modify input list'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            lst = ['hello', 'goodbye']
            _ = add_sizes(lst)

            return lst == ['hello', 'goodbye']

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)


TEST_CLASSES = [
    TestSingleString,
    TestTwoStrings,
    TestEmptyList,
    TestDoesNotModifyInput,
]
