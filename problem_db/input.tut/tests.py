import random
from string import ascii_lowercase as letters


class Test1(StudentTestCase):
    DESCRIPTION = "'reap', 'pear' -> 'reappear'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()
        self.run_in_student_context(_get_results, input_text='reap\npear\n')
        expected = 'reappear\n'
        self.assertEqual(self.standard_output, expected)

    def test_alternate(self):
        # randomness is the best way to test
        word1 = ''.join(random.choice(letters) for i in range(5))
        word2 = ''.join(random.choice(letters) for i in range(7))
        input_text = word1 + '\n' + word2 + '\n'
        expected = word1 + word2 + '\n'

        def _get_results():
            _function_under_test()

        self.run_in_student_context(_get_results, input_text=input_text)
        self.assertEqual(self.standard_output, expected)


class Test2(StudentTestCase):
    DESCRIPTION = "'Cat', 'Dog' -> 'CatDog'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()
        self.run_in_student_context(_get_results, input_text='Cat\nDog\n')
        expected = 'CatDog\n'
        self.assertEqual(self.standard_output, expected)

    def test_alternate(self):
        def _get_results():
            _function_under_test()
        self.run_in_student_context(_get_results, input_text='Bumble\nBee\n')
        expected = 'BumbleBee\n'
        self.assertEqual(self.standard_output, expected)


class Test3(StudentTestCase):
    DESCRIPTION = "'a', '' -> 'a'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            _function_under_test()
        self.run_in_student_context(_get_results, input_text='a\n\n')
        expected = 'a\n'
        self.assertEqual(self.standard_output, expected)

    def test_alternate(self):
        def _get_results():
            _function_under_test()
        self.run_in_student_context(_get_results, input_text='\nb\n')
        expected = 'b\n'
        self.assertEqual(self.standard_output, expected)


TEST_CLASSES = [
    Test1,
    Test2,
    Test3
]
