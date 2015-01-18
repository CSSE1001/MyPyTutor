class JustRunCodeAndDontTestAnything(StudentTestCase):
    DESCRIPTION = 'Code compiles'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pass

        _ = self.run_in_student_context(_get_results)


TEST_CLASSES = [
    JustRunCodeAndDontTestAnything,
]