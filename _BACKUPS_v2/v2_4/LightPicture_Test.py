import LightPicture as LP
import unittest


class TestConstructor_Coordinate(unittest.TestCase):
    """
        Test Coordinate class call
    """
    def test_none(self):
        """
            Calling Coordinates class with no key (kay = None)
        """
        c0 = LP.Coordinates()
        self.assertIsNot(c0, None)
        self.assertIsInstance(c0, LP.Coordinates)

    def test_iterable(self):
        """
            Calling Coordinates class with iterable key
        """
        c0 = LP.Coordinates([1])
        self.assertIsNot(c0, None)
        self.assertIsInstance(c0, LP.Coordinates)

        c1 = LP.Coordinates([1, 2, 3])
        self.assertIsNot(c1, None)
        self.assertIsInstance(c1, LP.Coordinates)

        c2 = LP.Coordinates('xyz')
        c3 = LP.Coordinates(['x', 'y', 'z', 5])
        self.assertIsNot(c2, None)
        self.assertIsInstance(c2, LP.Coordinates)


class TestConstructor_Vertex(unittest.TestCase):
    """
        Test Vertex class call
    """
    def test_none(self):
        """
            Calling Vertex class with no key (key = None)
        """
        v0 = LP.Vertex()
        self.assertIsNot(v0, None)
        self.assertIsInstance(v0, LP.Vertex)

    def test_iterable(self):
        """
            Calling Vertex class with iterable key
        """
        v0 = LP.Vertex([1])
        self.assertIsNot(v0, None)
        self.assertIsInstance(v0, LP.Vertex)

        v1 = LP.Vertex([1, 2, 3])
        self.assertIsNot(v1, None)
        self.assertIsInstance(v1, LP.Vertex)
        # check if Vertex has built a Coordinates object using the iterable passed as key
        self.assertIsInstance(v1.coordinates(), LP.Coordinates)

        v2 = LP.Vertex('xyz')
        self.assertIsNot(v2, None)
        self.assertIsInstance(v2, LP.Vertex)
        self.assertIsInstance(v2.coordinates(), LP.Coordinates)
        v3 = LP.Vertex(['x', 'y', 'z', 5])
        self.assertIsNot(v3, None)
        self.assertIsInstance(v3, LP.Vertex)
        self.assertIsInstance(v3.coordinates(), LP.Coordinates)


class TestConstructor_Triangle(unittest.TestCase):
    """
        Test Triangle class call
    """
    def test_none(self):
        """
            Calling Triangle class with no key (key = None)
        """
        t0 = LP.Triangle()
        self.assertIsNot(t0, None)
        self.assertIsInstance(t0, LP.Triangle)

    def test_iterable(self):
        """
            Calling Vertex class with iterable key
        """
        t0 = LP.Triangle([1])
        self.assertIsNot(t0, None)
        self.assertIsInstance(t0, LP.Triangle)

        t1 = LP.Triangle([1, 2, 3])
        self.assertIsNot(t1, None)
        self.assertIsInstance(t1, LP.Triangle)

        t2 = LP.Triangle('xyz')
        self.assertIsNot(t2, None)
        self.assertIsInstance(t2, LP.Vertex)

        t3 = LP.Triangle(['x', 'y', 'z', 5])
        self.assertIsNot(t3, None)
        self.assertIsInstance(t3, LP.Vertex)



class TestTemporary(unittest.TestCase):
    """
        Temporary tests or test currently in development
    """
    def test_draft(self):
        pass


if __name__ == '__main__':
    unittest.main()

