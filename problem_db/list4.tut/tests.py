class TestSingleNumber(StudentTestCase):
    DESCRIPTION = 'sum_elems([1]) -> 1'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_elems([1])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1)

    def test_alternate(self):
        def _get_results():
            return sum_elems([2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 2)


class TestTwoNumbers(StudentTestCase):
    DESCRIPTION = 'sum_elems([1, 2]) -> 3'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_elems([1, 2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 3)

    def test_alternate(self):
        def _get_results():
            return sum_elems([5, 5])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 10)


class TestEmptyList(StudentTestCase):
    DESCRIPTION = "sum_elems([]) -> 0"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return sum_elems([])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)


class TestDoesNotModifyInput(StudentTestCase):
    DESCRIPTION = 'does not modify input list'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            lst = [1, 2]
            _ = sum_elems(lst)

            return lst == [1, 2]

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)


TEST_CLASSES = [
    TestSingleNumber,
    TestTwoNumbers,
    TestEmptyList,
    TestDoesNotModifyInput,
]
