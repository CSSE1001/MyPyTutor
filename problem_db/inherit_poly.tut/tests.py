class TestRectangleArea(StudentTestCase):
    DESCRIPTION = 'r = Rectangle(4, 3); r.area() -> 12.'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            r = Rectangle(4, 3)
            return r.area()

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 12)

    def test_alternate(self):
        def _get_results():
            r = Rectangle(7, 2)
            return r.area()

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 14)


class TestRectangleVertices(StudentTestCase):
    DESCRIPTION = 'r = Rectangle(4, 3); r.vertices() -> [(0, 0), (0, 3), (4, 3), (4, 0)]'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            r = Rectangle(4, 3)
            return r.vertices()

        result = self.run_in_student_context(_get_results)
        expected = [(0, 0), (0, 3), (4, 3), (4, 0)]
        self.assertEqual(sorted(result), sorted(expected))

    def test_alternate(self):
        def _get_results():
            r = Rectangle(7, 2)
            return r.vertices()

        result = self.run_in_student_context(_get_results)
        expected = [(0, 0), (0, 2), (7, 2), (7, 0)]
        self.assertEqual(sorted(result), sorted(expected))


class TestTriangleArea(StudentTestCase):
    DESCRIPTION = 't = RightAngledTriangle([(0, 0), (0, 4), (3, 4)]); t.area() -> 6.'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            t = RightAngledTriangle([(0, 0), (0, 4), (3, 4)])
            return t.area()

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 6)

    def test_alternate(self):
        def _get_results():
            t = RightAngledTriangle([(0, 0), (0, 5), (12, 5)])
            return t.area()

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 30)


class TestTriangleVertices(StudentTestCase):
    DESCRIPTION = 't = RightAngledTriangle([(0, 0), (0, 4), (3, 4)]); t.vertices() -> [(0, 0), (0, 4), (3, 4)]'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            t = RightAngledTriangle([(0, 0), (0, 4), (3, 4)])
            return t.vertices()

        result = self.run_in_student_context(_get_results)
        expected = [(0, 0), (0, 4), (3, 4)]
        self.assertEqual(sorted(result), sorted(expected))

    def test_alternate(self):
        def _get_results():
            t = RightAngledTriangle([(0, 0), (0, 5), (12, 5)])
            return t.vertices()

        result = self.run_in_student_context(_get_results)
        expected = [(0, 0), (0, 5), (12, 5)]
        self.assertEqual(sorted(result), sorted(expected))


class TestMultipleRectangleArea(StudentTestCase):
    DESCRIPTION = 'r1 = Rectangle(2, 3); r2 = Rectangle(4, 5); total_area([r1, r2]) -> 26'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            r1 = Rectangle(2, 3)
            r2 = Rectangle(4, 5)
            return total_area([r1, r2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 26)

    def test_alternate(self):
        def _get_results():
            r1 = Rectangle(2, 9)
            r2 = Rectangle(4, 1)
            return total_area([r1, r2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, 22)


class TestMultipleRectangleVertices(StudentTestCase):
    DESCRIPTION = 'r1 = Rectangle(2, 3); r2 = Rectangle(4, 5); outer_bounds([r1, r2]) -> [(0, 0), (4, 5)]'
    MAIN_TEST = 'test_main'

    def test_main(self):
        def _get_results():
            r1 = Rectangle(2, 3)
            r2 = Rectangle(4, 5)
            return outer_bounds([r1, r2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [(0, 0), (4, 5)])

    def test_alternate(self):
        def _get_results():
            r1 = Rectangle(2, 9)
            r2 = Rectangle(4, 1)
            return outer_bounds([r1, r2])

        result = self.run_in_student_context(_get_results)
        self.assertEqual(result, [(0, 0), (4, 9)])


TEST_CLASSES = [
    TestRectangleArea,
    TestRectangleVertices,
    TestTriangleArea,
    TestTriangleVertices,
    TestMultipleRectangleArea,
    TestMultipleRectangleVertices,
]
