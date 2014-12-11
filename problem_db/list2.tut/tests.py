class List2TestResultIsList(StudentTestCase):
    DESCRIPTION = 'Result is a list'
    MAIN_TEST = 'test_result_is_list'

    def test_result_is_list(self):
        result = self.run_student_code([], 1)
        self.assertIsInstance(result, list)


class List2TestSingleBiggerElem(StudentTestCase):
    DESCRIPTION = 'all_gt([99], 1) -> [99]'
    MAIN_TEST = 'test_single_bigger_elem'

    def test_single_bigger_elem(self):
        result = self.run_student_code([99], 1)
        self.assertEqual(result, [99])

    def test_alternate(self):
        result = self.run_student_code([900], 150)
        self.assertEqual(result, [900])


class List2TestMultipleBiggerElems(StudentTestCase):
    DESCRIPTION = 'all_gt([5, 6], 1) -> [5, 6]'
    MAIN_TEST = 'test_two_bigger_elems'

    def test_two_bigger_elems(self):
        result = self.run_student_code([5, 6], 1)
        self.assertEqual(result, [5, 6])

    def test_alternate(self):
        result = self.run_student_code([10, 11], 1)
        self.assertEqual(result, [10, 11])


class List2TestMixed(StudentTestCase):
    DESCRIPTION = 'all_gt([1, 2, 3], 1) -> [2, 3]'
    MAIN_TEST = 'test_mixed'

    def test_mixed(self):
        result = self.run_student_code([1, 2, 3], 1)
        self.assertEqual(result, [2, 3])

    def test_alternate(self):
        result = self.run_student_code([1, 2, 3], 2)
        self.assertEqual(result, [3])


class List2TestEmptyList(StudentTestCase):
    DESCRIPTION = 'Correctly handles empty list'
    MAIN_TEST = 'test_empty_list'

    def test_empty_list(self):
        result = self.run_student_code([], 1)
        self.assertEqual(result, [])


class List2TestNoModificationOfArg(StudentTestCase):
    DESCRIPTION = "Doesn't modifiy input list"
    MAIN_TEST = 'test_input_list_safe'

    def test_input_list_safe(self):
        lst = [1, 2, 3, 4, 5]
        _ = self.run_student_code(lst, 3)
        self.assertEquals(lst, [1, 2, 3, 4, 5])

TEST_CLASSES = [
    List2TestResultIsList,
    List2TestSingleBiggerElem,
    List2TestMultipleBiggerElems,
    List2TestMixed,
    List2TestEmptyList,
    List2TestNoModificationOfArg,
]
