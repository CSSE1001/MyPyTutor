class TestAddNothing(StudentTestCase):
    DESCRIPTION = "d = {}; add_to_dict(d, []) -> [], d -> {}"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            d = {}
            result = add_to_dict(d, [])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {})
        self.assertEqual(result, [])


class TestAddSingleValueToEmptyDict(StudentTestCase):
    DESCRIPTION = "d = {}; add_to_dict(d, [('a', 2)]) -> [], d -> {'a': 2}"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            d = {}
            result = add_to_dict(d, [('a', 2)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'a': 2})
        self.assertEqual(result, [])

    def test_alternate(self):
        def _get_results():
            d = {}
            result = add_to_dict(d, [('b', 7)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'b': 7})
        self.assertEqual(result, [])


class TestAddSingleValue(StudentTestCase):
    DESCRIPTION = "d = {'b': 4}; add_to_dict(d, [('a', 2)]) -> [], d -> {'a': 2, 'b': 4}"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            d = {'b': 4}
            result = add_to_dict(d, [('a', 2)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'a': 2, 'b': 4})
        self.assertEqual(result, [])

    def test_alternate(self):
        def _get_results():
            d = {'a': 3}
            result = add_to_dict(d, [('b', 7)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'a': 3, 'b': 7})
        self.assertEqual(result, [])


class TestReplaceSingleValue(StudentTestCase):
    DESCRIPTION = "d = {'a': 0}; add_to_dict(d, [('a', 2)]) -> [('a', 0)], d -> {'a': 2}"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            d = {'a': 0}
            result = add_to_dict(d, [('a', 2)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'a': 2})
        self.assertEqual(result, [('a', 0)])

    def test_alternate(self):
        def _get_results():
            d = {'b': 3}
            result = add_to_dict(d, [('b', 7)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'b': 7})
        self.assertEqual(result, [('b', 3)])


class TestReplaceTwoValues(StudentTestCase):
    DESCRIPTION = "d = {'a': 0, 'b': 1}; add_to_dict(d, [('a', 2), ('b': 4)]) -> [('a', 0), ('b': 1)], d -> {'a': 2, 'b': 4}"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            d = {'a': 0, 'b': 1}
            result = add_to_dict(d, [('a', 2), ('b', 4)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'a': 2, 'b': 4})
        self.assertEqual(result, [('a', 0), ('b', 1)])

    def test_alternate(self):
        def _get_results():
            d = {'b': 3, 'c': 7}
            result = add_to_dict(d, [('b', 7), ('c', 2)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'b': 7, 'c': 2})
        self.assertEqual(result, [('b', 3), ('c', 7)])


class TestReplaceSameValueTwice(StudentTestCase):
    DESCRIPTION = "d = {'a': 0}; add_to_dict(d, [('a', 1), ('a': 2)]) -> [('a', 0), ('a': 1)], d -> {'a': 2}"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            d = {'a': 0}
            result = add_to_dict(d, [('a', 1), ('a', 2)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'a': 2})
        self.assertEqual(result, [('a', 0), ('a', 1)])

    def test_alternate(self):
        def _get_results():
            d = {'b': 3}
            result = add_to_dict(d, [('b', 7), ('b', 2)])
            return d, result

        d, result = self.run_in_student_context(_get_results)
        self.assertEqual(d, {'b': 2})
        self.assertEqual(result, [('b', 3), ('b', 7)])


TEST_CLASSES = [
    TestAddNothing,
    TestAddSingleValueToEmptyDict,
    TestAddSingleValue,
    TestReplaceSingleValue,
    TestReplaceTwoValues,
    TestReplaceSameValueTwice,
]
