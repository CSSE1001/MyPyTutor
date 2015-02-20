class TestBigs(StudentTestCase):
    DESCRIPTION = "big_keys({'a':24, 'e':30, 't':12, 'n':10}, 15) -> ['a', 'e']"
    MAIN_TEST = 'test_bigs'

    def test_bigs(self):
        def _get_results():
            value = big_keys({'a':24, 'e':30, 't':12, 'n':10}, 15)
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(sorted(value), ['a', 'e'])

    def test_alternate(self):
        def _get_results():
            value = big_keys({'a':24, 'e':30, 't':12, 'n':10}, 0)
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(sorted(value), ['a', 'e', 'n', 't'])

class TestEmptyResult(StudentTestCase):
    DESCRIPTION = "big_keys({'a':24, 'e':30, 't':12, 'n':10}, 99) -> []"
    MAIN_TEST = 'test_empty_result'

    def test_empty_result(self):
        def _get_results():
            value = big_keys({'a':24, 'e':30, 't':12, 'n':10}, 99)
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, [])

class TestEmptyDict(StudentTestCase):
    DESCRIPTION = "big_keys({}, 0) -> []"
    MAIN_TEST = 'test_empty_dict'

    def test_empty_dict(self):
        def _get_results():
            value = big_keys({}, 0)
            return value

        value = self.run_in_student_context(_get_results)
        self.assertEqual(value, [])





TEST_CLASSES = [
    TestBigs,
    TestEmptyResult,
    TestEmptyDict,
]
