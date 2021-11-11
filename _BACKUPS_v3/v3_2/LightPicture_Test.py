from LightPicture import *
import unittest


class TestConstructor_Vertex(unittest.TestCase):
    """
        Test Vertex class calls
    """
    def test_none(self):
        """
            Calling Vertex class with no key (key = None)
        """
        v0 = Vertex()
        self.assertIsNot(v0, None)
        self.assertIsInstance(v0, Vertex)

    def test_iterable_simple(self):
        """
            Calling Vertex class with key containing simple types
        """

        self.assertRaises(TypeError, Vertex, [1])
        self.assertRaises(TypeError, Vertex, ['asc'])

        v1 = Vertex([1, 2, 3])
        self.assertIsNot(v1, None)
        self.assertIsInstance(v1, Vertex)


        # v3 = Vertex(['x', 'y', 'z', 5])
        # self.assertIsNot(v3, None)
        # self.assertIsInstance(v3, Vertex)
        # self.assertIsInstance(v3.coordinates(), Coordinates)

    def test_iterable_specific(self):
        """
            Calling Vertex class with key containing specific types
        """

        # # Call Vertex class with Coordinate object as key
        # c = Coordinates()
        # v = Vertex(c)
        # self.assertIsInstance(v, Vertex)
        #
        # # # = = = = = = = = = = = = = = = = = = = = = = = = = = =
        # # #   Check auto reference building
        # # #    between Vertex and Coordinates
        # # # = = = = = = = = = = = = = = = = = = = = = = = = = = =
        # # Action: Vertex class call with Coordinate object as key
        # # Expect: Vertex object assigns Coordinates object as self coordinates
        # a_c0 = Coordinates([11, 12, 13])
        # a_v0 = Vertex(a_c0)
        # a_r0 = a_v0.coordinates()
        # self.assertIs(a_r0, a_c0)
        # # Action: Vertex class call with Coordinate object as key
        # # Expect: Vertex object is 'parent' of Coordinate object
        # b_c0 = Coordinates([11, 12, 13])
        # b_v0 = Vertex(b_c0)
        # b_r0 = b_c0.parents()
        # b_pass = b_v0 in b_r0
        # self.assertIs(b_pass, True)



class TestConstructor_Triangle(unittest.TestCase):
    """
        Test Triangle class call
    """
    def test_none(self):
        """
            Calling Triangle class with no key (key = None)
        """
        t0 = Triangle()
        self.assertIsNot(t0, None)
        self.assertIsInstance(t0, Triangle)

    def test_iterable(self):
        """
            Calling Vertex class with iterable key
        """
        # simple types iterables
        t1 = Triangle([1, 2, 3])
        self.assertIsNot(t1, None)
        self.assertIsInstance(t1, Triangle)
        t2 = Triangle('xyz')
        self.assertIsNot(t2, None)
        self.assertIsInstance(t2, Triangle)
        t3 = Triangle(['x', 'y', 'z'])
        self.assertIsNot(t3, None)
        self.assertIsInstance(t3, Triangle)

        # check vertices assignment
        t1 = Triangle([1001, 1002, 1003])
        self.assertIsNot(t1, None)
        self.assertIsInstance(t1, Triangle)
        result = t1.vertices()
        self.assertIsInstance(result, list)
        [r0, r1, r2] = result
        self.assertEqual(r0, 1001)
        self.assertEqual(r1, 1002)
        self.assertEqual(r2, 1003)

        t2 = Triangle('xyz')
        self.assertIsNot(t2, None)
        self.assertIsInstance(t2, Triangle)
        t3 = Triangle(['x', 'y', 'z'])
        self.assertIsNot(t3, None)
        self.assertIsInstance(t3, Triangle)



    def test_iterable_specific(self):
        """
            Calling Vertex class with key containing specific types
        """




class TestTemporary(unittest.TestCase):
    """
        Temporary tests or test currently in development
    """
    def test_draft(self):
        pass





if __name__ == '__main__':
    unittest.main()

