class TestSquare(StudentTestCase):
    DESCRIPTION = 'square(2) -> 4'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return square(2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)

    def test_alternate(self):
        def _get_results():
            return square(3)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 9)


class TestIsOddFalse(StudentTestCase):
    DESCRIPTION = 'is_odd(2) -> False'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return is_odd(2)

        result = self.run_in_student_context(_get_results)
        self.assertFalse(result)

    def test_alternate(self):
        def _get_results():
            return is_odd(4)

        result = self.run_in_student_context(_get_results)
        self.assertFalse(result)


class TestIsOddTrue(StudentTestCase):
    DESCRIPTION = 'is_odd(1) -> True'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return is_odd(1)

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)

    def test_alternate(self):
        def _get_results():
            return is_odd(5)

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)


class TestAdd(StudentTestCase):
    DESCRIPTION = 'add(1, 3) -> 4'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return add(1, 3)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)

    def test_alternate(self):
        def _get_results():
            return add(4, 5)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 9)


TEST_CLASSES = [
    TestSquare,
    TestIsOddFalse,
    TestIsOddTrue,
    TestAdd,
]
