class TestValidSingleDigitCommand(StudentTestCase):
    DESCRIPTION = "validate_input('add 2 3') -> ('add', [2., 3.])"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                student_result = validate_input('add 2 3')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertEqual(result, ('add', [2, 3]))

    def test_alternate(self):
        def _get_results():
            try:
                student_result = validate_input('mul 7 9')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertEqual(result, ('mul', [7, 9]))


class TestValidMultiDigitCommand(StudentTestCase):
    DESCRIPTION = "validate_input('div 78 123') -> ('div', [78., 123.])"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                student_result = validate_input('div 78 123')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertEqual(result, ('div', [78, 123]))

    def test_alternate(self):
        def _get_results():
            try:
                student_result = validate_input('mul 27 9')
                return student_result, False
            except Exception:
                return None, True

        result, raises = self.run_in_student_context(_get_results)

        if raises:
            self.fail('Your code must not raise an exception')

        self.assertEqual(result, ('mul', [27, 9]))


class TestInvalidCommandString(StudentTestCase):
    DESCRIPTION = "validate_input('banana 2 3') -> raises InvalidCommand()"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                validate_input('banana 2 3')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')

    def test_alternate(self):
        def _get_results():
            try:
                validate_input('stuff 2 3')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')


class TestInvalidNonFloatArguments(StudentTestCase):
    DESCRIPTION = "validate_input('add thingy 3') -> raises InvalidCommand()"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                validate_input('add thingy 3')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')

    def test_alternate(self):
        def _get_results():
            try:
                validate_input('add 29 stuff')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')


class TestInvalidNoArgs(StudentTestCase):
    DESCRIPTION = "validate_input('add') -> raises InvalidCommand()"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                validate_input('add')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')

    def test_alternate(self):
        def _get_results():
            try:
                validate_input('mul')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')


class TestInvalidOneArg(StudentTestCase):
    DESCRIPTION = "validate_input('add 2') -> raises InvalidCommand()"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                validate_input('add 2')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')

    def test_alternate(self):
        def _get_results():
            try:
                validate_input('mul 3')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')


class TestInvalidTooManyArgs(StudentTestCase):
    DESCRIPTION = "validate_input('add 2 3 4') -> raises InvalidCommand()"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            try:
                validate_input('add 2 3 4')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')

    def test_alternate(self):
        def _get_results():
            try:
                validate_input('mul 3 4 5 6 7')
            except InvalidCommand:
                return True
            return False

        raises = self.run_in_student_context(_get_results)

        if not raises:
            self.fail('Your code must raise InvalidCommand()')


TEST_CLASSES = [
    TestValidSingleDigitCommand,
    TestValidMultiDigitCommand,
    TestInvalidCommandString,
    TestInvalidNonFloatArguments,
    TestInvalidNoArgs,
    TestInvalidOneArg,
    TestInvalidTooManyArgs,
]
