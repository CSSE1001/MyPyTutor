class TestObj1Calls(StudentTestCase):
    DESCRIPTION = 'obj1 calls are printed correctly'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results)

        try:
            line = next(
                line for line in self.standard_output.splitlines()
                    if line.startswith('obj1')
            )
        except StopIteration:
            self.fail('No obj1 line printed')

        if line != 'obj1: C1.f, C1.g':
            self.fail('Incorrect obj1 line')


class TestObj2Calls(StudentTestCase):
    DESCRIPTION = 'obj2 calls are printed correctly'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results)

        try:
            line = next(
                line for line in self.standard_output.splitlines()
                if line.startswith('obj2')
            )
        except StopIteration:
            self.fail('No obj2 line printed')

        if line != 'obj2: C2.f, C1.g':
            self.fail('Incorrect obj2 line')


class TestObj3Calls(StudentTestCase):
    DESCRIPTION = 'obj3 calls are printed correctly'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results)

        try:
            line = next(
                line for line in self.standard_output.splitlines()
                if line.startswith('obj3')
            )
        except StopIteration:
            self.fail('No obj3 line printed')

        if line != 'obj3: C1.f, C3.g':
            self.fail('Incorrect obj3 line')


class TestObj4Calls(StudentTestCase):
    DESCRIPTION = 'obj4 calls are printed correctly'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()

        _ = self.run_in_student_context(_get_results)

        try:
            line = next(
                line for line in self.standard_output.splitlines()
                if line.startswith('obj4')
            )
        except StopIteration:
            self.fail('No obj4 line printed')

        if line != 'obj4: C4.f, C3.g':
            self.fail('Incorrect obj4 line')


TEST_CLASSES = [
    TestObj1Calls,
    TestObj2Calls,
    TestObj3Calls,
    TestObj4Calls,
]
