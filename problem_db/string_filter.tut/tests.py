class TestNoFilter(StudentTestCase):
    DESCRIPTION = "filter_string('python', '') -> 'python'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return filter_string('python', '')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'python')

    def test_alternate(self):
        def _get_results():
            return filter_string('monty', '')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'monty')


class TestEmptyInput(StudentTestCase):
    DESCRIPTION = "filter_string('', 'python') -> ''"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return filter_string('', 'python')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, '')


class TestSingleCharacterFilter(StudentTestCase):
    DESCRIPTION = "filter_string('python', 'y') -> 'pthon'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return filter_string('python', 'y')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'pthon')

    def test_alternate(self):
        def _get_results():
            return filter_string('monty', 'o')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'mnty')


class TestSingleCharacterRepeatedFilter(StudentTestCase):
    DESCRIPTION = "filter_string('hello', 'l') -> 'heo'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return filter_string('hello', 'l')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'heo')

    def test_alternate(self):
        def _get_results():
            return filter_string('baan', 'a')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'bn')


class TestMultipleCharacterFilter(StudentTestCase):
    DESCRIPTION = "filter_string('monty', 'ot') -> 'mny'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return filter_string('monty', 'ot')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'mny')

    def test_alternate(self):
        def _get_results():
            return filter_string('python', 'yh')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'pton')


class TestStripSentencePunctuation(StudentTestCase):
    DESCRIPTION = "filter_string('Blue.  No yel--  Auuuuuuuugh!', '.-!u') -> 'Ble  No yel  Agh'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            return filter_string('Blue.  No yel--  Auuuuuuuugh!', '.-!u')

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Ble  No yel  Agh')


TEST_CLASSES = [
    TestNoFilter,
    TestEmptyInput,
    TestSingleCharacterFilter,
    TestSingleCharacterRepeatedFilter,
    TestMultipleCharacterFilter,
    TestStripSentencePunctuation,
]
