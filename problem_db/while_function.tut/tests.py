class TestDiv35(StudentTestCase):
    DESCRIPTION = "div_3_5(7, 27) -> 9"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return div_3_5(7, 27)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 9)

    def test_alternate(self):
        def _get_results():
            return div_3_5(4, 12)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)

class TestDiv35StartDiv(StudentTestCase):
    DESCRIPTION = "div_3_5(6, 27) -> 10"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return div_3_5(6, 27)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 10)

    def test_alternate(self):
        def _get_results():
            return div_3_5(3, 12)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 5)

class TestDiv35EndDiv(StudentTestCase):
    DESCRIPTION = "div_3_5(7, 28) -> 10"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return div_3_5(7, 28)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 10)

    def test_alternate(self):
        def _get_results():
            return div_3_5(4, 12)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 4)

class TestDiv35Empty(StudentTestCase):
    DESCRIPTION = "div_3_5(6, 6) -> 0"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return div_3_5(6, 6)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)

    def test_alternate(self):
        def _get_results():
            return div_3_5(3, 3)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0)



TEST_CLASSES = [
    TestDiv35,
    TestDiv35StartDiv,
    TestDiv35EndDiv,
    TestDiv35Empty
]
