class PointIsDefined(StudentTestCase):
    DESCRIPTION = 'Defined Point class'
    MAIN_TEST = 'test_defined'

    def test_defined(self):
        def _get_results():
            try:
                Point
            except NameError:
                return False
            return True

        is_defined = self.run_in_student_context(_get_results)
        self.assertTrue(is_defined)


class DistanceToSelf(StudentTestCase):
    DESCRIPTION = 'pt = Point(2, 3); pt.dist_to_point(pt) -> 0.'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pt = Point(2, 3)

            return pt.dist_to_point(pt)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 0.)


class DistanceToOrigin(StudentTestCase):
    DESCRIPTION = 'origin = Point(0, 0); pt = Point(3, 4); origin.dist_to_point(pt) -> 5.'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            origin = Point(0, 0)
            pt = Point(3, 4)

            return origin.dist_to_point(pt)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 5.)

    def test_alternate(self):
        def _get_results():
            origin = Point(0, 0)
            pt = Point(5, 12)

            return origin.dist_to_point(pt)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 13.)


class DistanceBetweenPoints(StudentTestCase):
    DESCRIPTION = 'pt1 = Point(1, 2); pt2 = Point(3, 4); pt1.dist_to_point(pt2) -> 2.828427'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pt1 = Point(1, 2)
            pt2 = Point(3, 4)

            return pt1.dist_to_point(pt2)

        import math
        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, math.sqrt(8))

    def test_alternate(self):
        def _get_results():
            pt1 = Point(1, 1)
            pt2 = Point(5, 5)

            return pt1.dist_to_point(pt2)

        import math
        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, math.sqrt(32))


class PointIsNearSelf(StudentTestCase):
    DESCRIPTION = 'pt = Point(2, 3); pt.is_near(pt) -> True'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pt = Point(2, 3)

            return pt.is_near(pt)

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)


class PointIsFar(StudentTestCase):
    DESCRIPTION = 'pt1 = Point(1, 2); pt2 = Point(3, 4); pt1.is_near(pt2) -> False'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pt1 = Point(1, 2)
            pt2 = Point(3, 4)

            return pt1.is_near(pt2)

        result = self.run_in_student_context(_get_results)
        self.assertFalse(result)

    def test_alternate(self):
        def _get_results():
            pt1 = Point(1, 1)
            pt2 = Point(5, 5)

            return pt1.is_near(pt2)

        result = self.run_in_student_context(_get_results)
        self.assertFalse(result)


class PointIsClose(StudentTestCase):
    DESCRIPTION = 'pt1 = Point(1, 2); pt2 = Point(1 + 1e-9, 2 + 1e-9); pt1.is_near(pt2) -> True'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pt1 = Point(1, 2)
            pt2 = Point(1 + 1e-9, 2 + 1e-9)

            return pt1.is_near(pt2)

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)

    def test_alternate(self):
        def _get_results():
            pt1 = Point(3, 3)
            pt2 = Point(3 + 1e-9, 3 + 1e-9)

            return pt1.is_near(pt2)

        result = self.run_in_student_context(_get_results)
        self.assertTrue(result)


class AddOriginToPoint(StudentTestCase):
    DESCRIPTION = "origin = Point(0, 0); pt = Point(2, 3); pt.add_point(origin); print(pt) -> 'Point(2, 3)'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            origin = Point(0, 0)
            pt = Point(2, 3)

            pt.add_point(origin)
            return repr(pt)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Point(2, 3)')

    def test_alternate(self):
        def _get_results():
            origin = Point(0, 0)
            pt = Point(13, 14)

            pt.add_point(origin)
            return repr(pt)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Point(13, 14)')


class AddTwoPoints(StudentTestCase):
    DESCRIPTION = "pt1 = Point(1, 2); pt2 = Point(3, 4); pt1.add_point(pt2); print(pt1) -> 'Point(4, 6)'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pt1 = Point(1, 2)
            pt2 = Point(3, 4)

            pt1.add_point(pt2)
            return repr(pt1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Point(4, 6)')

    def test_alternate(self):
        def _get_results():
            pt1 = Point(6, 6)
            pt2 = Point(4, 4)

            pt1.add_point(pt2)
            return repr(pt1)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Point(10, 10)')


class PointGivenAsArgumentDoesNotChange(StudentTestCase):
    DESCRIPTION = "pt1 = Point(1, 2); pt2 = Point(3, 4); pt1.add_point(pt2); print(pt2) -> 'Point(3, 4)'"
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            pt1 = Point(1, 2)
            pt2 = Point(3, 4)

            pt1.add_point(pt2)
            return repr(pt2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Point(3, 4)')

    def test_alternate(self):
        def _get_results():
            pt1 = Point(6, 6)
            pt2 = Point(4, 4)

            pt1.add_point(pt2)
            return repr(pt2)

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 'Point(4, 4)')


TEST_CLASSES = [
    PointIsDefined,
    DistanceToSelf,
    DistanceToOrigin,
    DistanceBetweenPoints,
    PointIsNearSelf,
    PointIsFar,
    PointIsClose,
    AddOriginToPoint,
    AddTwoPoints,
    PointGivenAsArgumentDoesNotChange,
]
