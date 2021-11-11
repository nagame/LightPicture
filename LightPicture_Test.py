from LightPicture import *
import unittest
import random
import time


"""
Sandbox for unittest
There are some tests here for checking LightPicture or mesh objects.
It is not complete.
"""

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

        # self.assertRaises(TypeError, Vertex, [1])
        # self.assertRaises(TypeError, Vertex, ['asc'])

        v1 = Vertex([1, 2, 3])
        self.assertIsNot(v1, None)
        self.assertIsInstance(v1, Vertex)

    def test_iterable_specific(self):
        """
            Calling Vertex class with key containing specific types
        """
        # Call Vertex class with Triangle object as key
        t = Triangle()
        v = Vertex(t)
        self.assertIsInstance(v, Vertex)
        v_parents = v.parents()
        self.assertTrue(t in v_parents)


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

        # create triangle using iterable of Vertex
        v0 = Vertex([0, 0, 0])
        v1 = Vertex([1, 1, 1])
        v2 = Vertex([2, 2, 2])
        t0 = Triangle([v0, v1, v2])
        self.assertIsInstance(t0, Triangle)
        vertices = t0.vertices()
        self.assertIs(v0, vertices[0])
        self.assertIs(v1, vertices[1])
        self.assertIs(v2, vertices[2])

        # create Triangle recursive Vertex construction
        t1 = Triangle([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ])
        self.assertIsInstance(t1, Triangle)
        vertices = t1.vertices()
        cv_0 = vertices[0].coordinates()
        cv_1 = vertices[1].coordinates()
        cv_2 = vertices[2].coordinates()
        self.assertEqual([1, 2, 3], cv_0)
        self.assertEqual([4, 5, 6], cv_1)
        self.assertEqual([7, 8, 9], cv_2)


class TestConstructor_TriangleMesh(unittest.TestCase):
    """
        Test Triangle class call
    """
    def test_none(self):
        """
            Calling TriangleMesh class with no key (key = None)
        """
        m = TriangleMesh()
        self.assertIsInstance(m, TriangleMesh)

    def test_iterable(self):
        """
            Calling TriangleMesh class with iterable key
        """
        t0 = Triangle()
        t1 = Triangle()
        t2 = Triangle()
        m0 = TriangleMesh([t0, t1, t2])
        m0_triangles = m0.triangles()
        self.assertIs(t0, m0_triangles[0])
        self.assertIs(t1, m0_triangles[1])
        self.assertIs(t2, m0_triangles[2])

    def test_iterable_specific(self):
        """
            Calling TriangleMesh class with key containing specific types
        """
        # check TriangleMesh constructor with triangles as key
        t0 = Triangle([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        t1 = Triangle([[3, 3, 3], [4, 4, 4], [5, 5, 5]])
        t2 = Triangle([[6, 6, 6], [7, 7, 7], [8, 8, 8]])
        m0 = TriangleMesh([t0, t1, t2])
        m0_triangles = m0.triangles()
        self.assertIs(t0, m0_triangles[0])
        self.assertIs(t1, m0_triangles[1])
        self.assertIs(t2, m0_triangles[2])
        t0_v = m0_triangles[0].vertices()
        t1_v = m0_triangles[1].vertices()
        t2_v = m0_triangles[2].vertices()
        self.assertEqual(t0_v[0].coordinates(), [0, 0, 0])
        self.assertEqual(t0_v[1].coordinates(), [1, 1, 1])
        self.assertEqual(t0_v[2].coordinates(), [2, 2, 2])
        self.assertEqual(t1_v[0].coordinates(), [3, 3, 3])
        self.assertEqual(t1_v[1].coordinates(), [4, 4, 4])
        self.assertEqual(t1_v[2].coordinates(), [5, 5, 5])
        self.assertEqual(t2_v[0].coordinates(), [6, 6, 6])
        self.assertEqual(t2_v[1].coordinates(), [7, 7, 7])
        self.assertEqual(t2_v[2].coordinates(), [8, 8, 8])


class TestTemporary(unittest.TestCase):
    """
        Temporary tests or test currently in development
    """
    def test_draft(self):
        pass

    def test_draft2(self):
        pass
        # # test with every triangle having distinct vertices
        # t0 = Triangle([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        # t1 = Triangle([[3, 3, 3], [4, 4, 4], [5, 5, 5]])
        # t2 = Triangle([[6, 6, 6], [7, 7, 7], [8, 8, 8]])
        # m0 = TriangleMesh([t0, t1, t2])
        # writer = Xml3mfWriter(m0)
        # writer.write()

    def test_draft2(self):
        pass
        # # test with common vertex objects between triangels
        # v0 = Vertex([0, 0, 0])
        # v1 = Vertex([1, 1, 1])
        # v2 = Vertex([2, 2, 2])
        # t0 = Triangle([v0, v1, v2])
        # t1 = Triangle([v0, v2, v2])
        # t2 = Triangle([v0, v0, v0])
        # t3 = Triangle([v0, v1, v0])
        #
        # # throw in another 'dynamic' triangle
        # t4 = Triangle([[6, 6, 6], [7, 7, 7], [8, 8, 8]])
        #
        # m0 = TriangleMesh([t0, t1, t2, t3, t4])
        #
        # writer = Xml3mfWriter(m0)
        # writer.write_triangle_mesh()

    def test_create_sample_file(self):
        pass
        # # create list of triangles defined by 3 points in space [p1, p2, p3]
        # # the order of points is important
        # triangles = [ [[x, x, x], [x+1, x+1, x+1], [x+2, x+2, x+2]] for x in range(3) ]
        #
        # # create mesh builder object
        # # it will keep track of 'used points in space' and generate Triangle and Vertex objects and connect them
        # # this abstraction layer allows us to free from thinking about which point have already been used
        # # and the objects structure for writing 3mf file is being created 'on the fly'
        # # pass [x, y, z] as space size
        # tmb = TriangleMeshBuilder([200, 200, 200])
        # # give all triangles to the mesh builder
        # for t in triangles:
        #     tmb.triangle(t)
        #
        # tmb.write_3mf_file()
        #
        # # # # alternative way of  doing the above by hand
        # # # get the mesh from the builder
        # # mesh = tmb.triangle_mesh
        # # # create 3mf writer
        # # writer = Xml3mfWriter(mesh)
        # # # give the created mesh to the writer
        # # writer.write_triangle_mesh()

    def test_create_sample_file_2(self):
        pass
        # # create list of triangles defined by 3 points in space [p1, p2, p3]
        # # the order of points is important
        #
        # triangles = [ [[x%400, x%400, x%400], [(x+1)%400, (x+1)%400, (x+1)%400], [(x+2)%400, (x+2)%400, (x+2)%400]] \
        #               for x in range(1000) ]
        # # triangles = [[[1, 1, 1], [1, 1, 1], [1, 1, 1]] for x in range(10)]
        #
        # # create mesh builder object
        # # it will keep track of 'used points in space' and generate Triangle and Vertex objects and connect them
        # # this abstraction layer allows us to free from thinking about which point have already been used
        # # and the objects structure for writing 3mf file is being created 'on the fly'
        # # pass [x, y, z] as space size
        # tmb = TriangleMeshBuilder([400, 400, 400])
        # # give all triangles to the mesh builder
        # for t in triangles:
        #     tmb.triangle(t)
        #
        # tmb.write_3mf_file()

    def test_create_sample_mesh(self):
        pass
        # # create list of triangles defined by 3 points in space [p1, p2, p3]
        # # the order of points is important
        #
        # # [
        # #     [], [], []
        # # ],
        #
        # triangles = [
        #     [
        #         [0, 0, 0], [10, 0, 0], [5, 5, 0]
        #     ],
        #     [
        #         [0, 0, 0], [5, 5, 0], [2, 2, 20]
        #     ],
        #     [
        #         [2, 2, 20], [5, 5, 0], [10, 0, 0]
        #     ],
        #     [
        #         [0, 0, 0], [2, 2, 20], [10, 0, 0]
        #     ]
        # ]
        #
        #
        # # create mesh builder object
        # tmb = TriangleMeshBuilder([400, 400, 400])
        # # give all triangles to the mesh builder
        # for t in triangles:
        #     tmb.triangle(t)
        #
        # tmb.write_3mf_file()

    def test_random_big_file(self):
        pass
        # # generate a significant amount of triangels and save them to 3mf

        # # generate random triangels
        # t0 = time.perf_counter()
        # rand = random.random
        # for n in range(100_000):
        #     triangles.append([
        #         [int(rand() * x), int(rand() * y), int(rand() * z)],
        #         [int(rand() * x), int(rand() * y), int(rand() * z)],
        #         [int(rand() * x), int(rand() * y), int(rand() * z)]
        #     ])
        # t0 = time.perf_counter() - t0
        #
        # # create mesh builder object
        # t1 = time.perf_counter()
        # tmb = TriangleMeshBuilder([x, y, z])
        # t1 = time.perf_counter() - t1
        #
        # # give all triangles to the mesh builder
        # t2 = time.perf_counter()
        # for t in triangles:
        #     tmb.triangle(t)
        # t2 = time.perf_counter() - t2
        #
        # # build xml structure
        # t3 = time.perf_counter()
        # tmb.mesh_to_xml()
        # t3 = time.perf_counter() - t3
        #
        # # save 3mf file
        # t4 = time.perf_counter()
        # tmb.save_3mf()
        # t4 = time.perf_counter() - t4


if __name__ == '__main__':
    unittest.main()

