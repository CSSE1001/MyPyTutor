class RectangleIsDefined(StudentTestCase):
    DESCRIPTION = 'Defined Rectangle class'
    MAIN_TEST = 'test_defined'

    def test_defined(self):
        def _get_results():
            return Rectangle((0, 0), 1, 1)

        try:
            _ = self.run_in_student_context(_get_results)
        except NameError:
            self.fail('Rectangle not defined')


class CanGetBottomRight(StudentTestCase):
    DESCRIPTION = 'Rectangle((0, 0), 1, 1).get_bottom_right() -> (1, 1)'
    MAIN_TEST = 'test_get_bottom_right'

    def test_get_bottom_right(self):
        def _get_results():
            rect = Rectangle((0, 0), 1, 1)
            return rect.get_bottom_right()

        bottom_right = self.run_in_student_context(_get_results)
        self.assertEqual(bottom_right, (1, 1))

    def test_alternate(self):
        def _get_results():
            rect = Rectangle((0, 0), 2, 3)
            return rect.get_bottom_right()

        bottom_right = self.run_in_student_context(_get_results)
        self.assertEqual(bottom_right, (2, 3))


# TODO: bottom right with non-zero point
# TODO: move
# TODO: etc etc...

TEST_CLASSES = [
    RectangleIsDefined,
    CanGetBottomRight,
]

