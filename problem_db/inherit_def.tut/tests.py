class WorkerIsDefined(StudentTestCase):
    DESCRIPTION = 'Defined Worker class'
    MAIN_TEST = 'test_defined'

    def test_defined(self):
        def _get_results():
            try:
                Worker
            except NameError:
                return False
            return True

        is_defined = self.run_in_student_context(_get_results)
        self.assertTrue(is_defined)


class WorkerReturnsManager(StudentTestCase):
    DESCRIPTION = "bob = Employee('Bob', 500); joe = Worker('Joe', 1000, bob); joe.get_manager() -> bob"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            bob = Employee('Bob', 500)
            joe = Worker('Joe', 1000, bob)

            return bob, joe

        manager, employee = self.run_in_student_context(_get_results)

        self.assertEqual(employee.get_manager(), manager)


class ExecutiveIsDefined(StudentTestCase):
    DESCRIPTION = 'Defined Executive class'
    MAIN_TEST = 'test_defined'

    def test_defined(self):
        def _get_results():
            try:
                Executive
            except NameError:
                return False
            return True

        is_defined = self.run_in_student_context(_get_results)
        self.assertTrue(is_defined)


class ExecutiveCalculatesWage(StudentTestCase):
    DESCRIPTION = "mary = Executive('Mary', 26000, 5200); mary.wage() -> 1200."
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            mary = Executive('Mary', 26000, 5200)

            return mary

        mary = self.run_in_student_context(_get_results)

        self.assertEqual(mary.wage(), 1200)

    def test_alternate(self):
        def _get_results():
            mary = Executive('Mary', 52000, 2600)

            return mary

        mary = self.run_in_student_context(_get_results)

        self.assertEqual(mary.wage(), 2100)


TEST_CLASSES = [
    WorkerIsDefined,
    WorkerReturnsManager,
    ExecutiveIsDefined,
    ExecutiveCalculatesWage,
]
