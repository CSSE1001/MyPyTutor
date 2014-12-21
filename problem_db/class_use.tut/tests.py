class PrintsInfoWithoutFriends(StudentTestCase):
    DESCRIPTION = "bob = Person('Bob Smith', 40, 'M'); print_friend_info(bob)"
    MAIN_TEST = 'test_bob'

    def test_bob(self):
        def _get_results():
            bob = Person('Bob Smith', 40, 'M')
            print_friend_info(bob)

        _ = self.run_in_student_context(_get_results)

        expected_output = 'Bob Smith\n40\n'
        self.assertEqual(self.standard_output, expected_output)

    def test_alternate(self):
        def _get_results():
            jane = Person('Jane Bloggs', 9, 'F')
            print_friend_info(jane)

        _ = self.run_in_student_context(_get_results)

        expected_output = 'Jane Bloggs\n9\n'
        self.assertEqual(self.standard_output, expected_output)


class PrintsInfoWithFriends(StudentTestCase):
    DESCRIPTION = "ed = Person('Ed', 8, 'M'); bob.set_friend(ed); print_friend_info(bob)"
    MAIN_TEST = 'test_bob'

    def test_bob(self):
        def _get_results():
            bob = Person('Bob Smith', 40, 'M')
            ed = Person('Ed', 8, 'M')
            bob.set_friend(ed)

            print_friend_info(bob)

        _ = self.run_in_student_context(_get_results)

        expected_output = 'Bob Smith\n40\nFriends with Ed\n'
        self.assertEqual(self.standard_output, expected_output)

    def test_alternate(self):
        def _get_results():
            jane = Person('Jane Bloggs', 9, 'F')
            jo = Person('Joseph', 8, 'M')
            jane.set_friend(jo)

            print_friend_info(jane)

        _ = self.run_in_student_context(_get_results)

        expected_output = 'Jane Bloggs\n9\nFriends with Joseph\n'
        self.assertEqual(self.standard_output, expected_output)


class CreatesFry(StudentTestCase):
    DESCRIPTION = "fry = create_fry(); str(fry) -> 'Mr Philip J. Fry 25'"
    MAIN_TEST = 'test_string_output'

    def test_string_output(self):
        def _get_results():
            fry = create_fry()
            return fry

        fry = self.run_in_student_context(_get_results)
        self.assertEqual(str(fry), 'Mr Philip J. Fry 25')

    def test_getters(self):
        def _get_results():
            fry = create_fry()
            return fry

        fry = self.run_in_student_context(_get_results)

        self.assertEqual(fry.get_name(), 'Philip J. Fry')
        self.assertEqual(fry.get_age(), 25)
        self.assertEqual(fry.get_gender(), 'M')


class MakesFriends(StudentTestCase):
    DESCRIPTION = "leela = Person('T. Leela', 22, 'F'); make_friends(fry, leela)"
    MAIN_TEST = 'test_make_friends'

    def test_make_friends(self):
        def _get_results():
            fry = Person('Philip J. Fry', 25, 'M')
            leela = Person('T. Leela', 22, 'F')

            make_friends(fry, leela)

            return fry, leela

        fry, leela = self.run_in_student_context(_get_results)
        self.assertEqual(fry.get_friend(), leela)
        self.assertEqual(leela.get_friend(), fry)


TEST_CLASSES = [
    PrintsInfoWithoutFriends,
    PrintsInfoWithFriends,
    CreatesFry,
    MakesFriends,
]
