class SingleElementTrue(StudentTestCase):
    DESCRIPTION = 'has_gt([1], 0) -> True'
    MAIN_TEST = 'test_single_element_true'

    def test_single_element_true(self):
        def _get_results():
            return has_gt([1], 0)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertTrue(result)

    def test_alternate(self):
        def _get_results():
            return has_gt([2], 1)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertTrue(result)


class SingleElementFalse(StudentTestCase):
    DESCRIPTION = 'has_gt([1], l) -> False'
    MAIN_TEST = 'test_single_element_false'

    def test_single_element_false(self):
        def _get_results():
            return has_gt([1], 1)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertFalse(result)

    def test_alternate(self):
        def _get_results():
            return has_gt([2], 2)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertFalse(result)


class MultipleElementsAllTrue(StudentTestCase):
    DESCRIPTION = 'has_gt([1, 2], 0) -> True'
    MAIN_TEST = 'test_multiple_elements_all_true'

    def test_multiple_elements_all_true(self):
        def _get_results():
            return has_gt([1, 2], 0)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertTrue(result)

    def test_alternate(self):
        def _get_results():
            return has_gt([2, 3], 1)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertTrue(result)


class MultipleElementsAllFalse(StudentTestCase):
    DESCRIPTION = 'has_gt([1, 2], 3) -> False'
    MAIN_TEST = 'test_multiple_elements_all_false'

    def test_multiple_elements_all_false(self):
        def _get_results():
            return has_gt([1, 2], 3)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertFalse(result)

    def test_alternate(self):
        def _get_results():
            return has_gt([2, 3], 4)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertFalse(result)


class MultipleElementsMixedTrue(StudentTestCase):
    DESCRIPTION = 'has_gt([1, 2, 3], 2) -> True'
    MAIN_TEST = 'test_multiple_elements_mixed_true'

    def test_multiple_elements_mixed_true(self):
        def _get_results():
            return has_gt([1, 2, 3], 2)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertTrue(result)

    def test_alternate(self):
        def _get_results():
            return has_gt([2, 3, 4], 3)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertTrue(result)


class MultipleElementsMixedFalse(StudentTestCase):
    DESCRIPTION = 'has_gt([1, 2, 3], 5) -> True'
    MAIN_TEST = 'test_multiple_elements_mixed_false'

    def test_multiple_elements_mixed_false(self):
        def _get_results():
            return has_gt([1, 2, 3], 5)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertFalse(result)

    def test_alternate(self):
        def _get_results():
            return has_gt([2, 3, 4], 5)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertFalse(result)


class EmptyList(StudentTestCase):
    DESCRIPTION = 'has_gt([], 0) -> False'
    MAIN_TEST = 'test_empty_list'

    def test_empty_list(self):
        def _get_results():
            return has_gt([], 0)

        result = self.run_in_student_context(_get_results)
        self.assertIsInstance(result, bool)  # avoid implicit None => False
        self.assertFalse(result)


TEST_CLASSES = [
    SingleElementTrue,
    SingleElementFalse,
    MultipleElementsAllTrue,
    MultipleElementsAllFalse,
    MultipleElementsMixedTrue,
    MultipleElementsMixedFalse,
    EmptyList,
]
