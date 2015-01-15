class TestEmptyIndices(StudentTestCase):
    DESCRIPTION = 'recursive_index([1, [2], 3], []) -> [1, [2], 3]'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return recursive_index([1, [2], 3], [])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [1, [2], 3])

    def test_alternate(self):
        def _get_results():
            return recursive_index([4], [])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [4])


class TestSingleLevelIndex(StudentTestCase):
    DESCRIPTION = 'recursive_index([1, [2], 3], [0]) -> 1'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return recursive_index([1, [2], 3], [0])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 1)

    def test_alternate(self):
        def _get_results():
            return recursive_index([4], [0])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)


class TestSingleLevelOfNesting(StudentTestCase):
    DESCRIPTION = 'recursive_index([1, [2], 3], [1, 0]) -> 2'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return recursive_index([1, [2], 3], [1, 0])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 2)

    def test_alternate(self):
        def _get_results():
            return recursive_index([[4]], [0, 0])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)


class TestComplexList(StudentTestCase):
    DESCRIPTION = 'recursive_index([[1, 2], [[3], 4], [5, 6], 7], [1, 0, 0]) -> 3'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return recursive_index([[1, 2], [[3], 4], [5, 6], 7], [1, 0, 0])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 3)

    def test_alternate(self):
        def _get_results():
            return recursive_index([[4], 5, [6, [7]]], [2, 1, 0])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 7)


class TestNegativeIndices(StudentTestCase):
    DESCRIPTION = 'recursive_index([[1, 2], [[3], 4], [5, 6], 7], [-2, -1]) -> 6'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return recursive_index([[1, 2], [[3], 4], [5, 6], 7], [-2, -1])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 6)

    def test_alternate(self):
        def _get_results():
            return recursive_index([[4], 5, [6, [7]]], [-1, -1, -1])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 7)


class TestDoesNotModifyLst(StudentTestCase):
    DESCRIPTION = 'does not modify lst'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            lst = [1, 2]
            _ = recursive_index(lst, [])

            return lst == [1, 2]

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)


class TestDoesNotModifyIndexPath(StudentTestCase):
    DESCRIPTION = 'does not modify index_path'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            path = [0, 0]
            _ = recursive_index([[1]], path)

            return path == [0, 0]

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)


TEST_CLASSES = [
    TestEmptyIndices,
    TestSingleLevelIndex,
    TestSingleLevelOfNesting,
    TestComplexList,
    TestNegativeIndices,
    TestDoesNotModifyLst,
    TestDoesNotModifyIndexPath,
]
