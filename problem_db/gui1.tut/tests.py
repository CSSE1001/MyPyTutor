class JustRunCodeAndDontTestAnything(StudentTestCase):
    DESCRIPTION = 'Code compiles'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _show_student_code():
            window, frame = _get_window()
            create_layout(frame)

        _ = self.run_in_student_context(_show_student_code)


TEST_CLASSES = [
    JustRunCodeAndDontTestAnything,
]