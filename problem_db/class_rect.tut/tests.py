class RectangleIsDefined(StudentTestCase):
    DESCRIPTION = 'Defined Rectangle class'
    MAIN_TEST = 'test_defined'

    def test_defined(self):
        def _get_results():
            try:
                Rectangle
            except NameError:
                return False
            return True

        is_defined = self.run_in_student_context(_get_results)
        self.assertTrue(is_defined)


class CanGetBottomRightFromOrigin(StudentTestCase):
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


class CanGetBottomRightGenerally(StudentTestCase):
    DESCRIPTION = 'Rectangle((2, 3), 2, 1).get_bottom_right() -> (4, 4)'
    MAIN_TEST = 'test_get_bottom_right'

    def test_get_bottom_right(self):
        def _get_results():
            rect = Rectangle((2, 3), 2, 1)
            return rect.get_bottom_right()

        bottom_right = self.run_in_student_context(_get_results)
        self.assertEqual(bottom_right, (4, 4))

    def test_alternate(self):
        def _get_results():
            rect = Rectangle((8, 7), 2, 3)
            return rect.get_bottom_right()

        bottom_right = self.run_in_student_context(_get_results)
        self.assertEqual(bottom_right, (10, 10))


class StrMethodWorksInitially(StudentTestCase):
    DESCRIPTION = "str(Rectangle((0, 0), 1, 1)) -> '((0, 0), (1, 1))'"
    MAIN_TEST = 'test_str'

    def test_str(self):
        def _get_results():
            rect = Rectangle((0, 0), 1, 1)
            return str(rect)

        s = self.run_in_student_context(_get_results)
        self.assertEqual(s, '((0, 0), (1, 1))')

    def test_alternate(self):
        def _get_results():
            rect = Rectangle((2, 7), 1, 1)
            return str(rect)

        s = self.run_in_student_context(_get_results)
        self.assertEqual(s, '((2, 7), (3, 8))')


class MoveMethodWorks(StudentTestCase):
    DESCRIPTION = "r = Rectangle((0, 0), 1, 1); r.move((2, 2)); str(r) -> '((2, 2), (3, 3))'"
    MAIN_TEST = 'test_move'

    def test_move(self):
        def _get_results():
            rect = Rectangle((0, 0), 1, 1)
            rect.move((2, 2))
            return str(rect)

        s = self.run_in_student_context(_get_results)
        self.assertEqual(s, '((2, 2), (3, 3))')

    def test_alternate(self):
        def _get_results():
            rect = Rectangle((2, 7), 1, 1)
            rect.move((3, 4))
            return str(rect)

        s = self.run_in_student_context(_get_results)
        self.assertEqual(s, '((3, 4), (4, 5))')


class ResizeMethodWorks(StudentTestCase):
    DESCRIPTION = "r = Rectangle((0, 0), 1, 1); r.resize(2, 2); str(r) -> '((0, 0), (2, 2))'"
    MAIN_TEST = 'test_resize'

    def test_resize(self):
        def _get_results():
            rect = Rectangle((0, 0), 1, 1)
            rect.resize(2, 2)
            return str(rect)

        s = self.run_in_student_context(_get_results)
        self.assertEqual(s, '((0, 0), (2, 2))')

    def test_alternate(self):
        def _get_results():
            rect = Rectangle((2, 7), 1, 1)
            rect.resize(3, 4)
            return str(rect)

        s = self.run_in_student_context(_get_results)
        self.assertEqual(s, '((2, 7), (5, 11))')


# TODO: bottom right with non-zero point
# TODO: move
# TODO: etc etc...

TEST_CLASSES = [
    RectangleIsDefined,
    CanGetBottomRightFromOrigin,
    CanGetBottomRightGenerally,
    StrMethodWorksInitially,
    MoveMethodWorks,
    ResizeMethodWorks,
]

