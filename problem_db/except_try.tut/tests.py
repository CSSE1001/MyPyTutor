class TestValidInt(StudentTestCase):
    DESCRIPTION = "try_int('2') -> 2"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                student_result = try_int('2')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertEqual(result, 2)

    def test_alternate(self):
        def _get_results():
            try:
                student_result = try_int('2234')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertEqual(result, 2234)


class TestInvalidInt(StudentTestCase):
    DESCRIPTION = "try_int('banana') -> None"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                student_result = try_int('banana')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertIsNone(result)

    def test_alternate(self):
        def _get_results():
            try:
                student_result = try_int('hammock')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertIsNone(result)


TEST_CLASSES = [
    TestValidInt,
    TestInvalidInt,
]
