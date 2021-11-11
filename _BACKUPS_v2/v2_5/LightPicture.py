from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil
import timeit
import subprocess


class Coordinates:
    """
    Abstract coordinate vector
    """
    def __init__(self, key=None):
        self.point = self._point  # point: iterable
        self._self_point = [None]  # Actual self point

        self.parents = self._parents  # Interpret key in 'parent' context
        self._self_parents = set()  # Set of own parents

        self.scale = self._scale  # Return scaled Coordinate
        self.translate = self._translate  # Return translated Coordinate e

        # try interpreting the key in the context of point
        key_valid = False
        try:
            key_valid = self._point(key)
        except Exception as e:
            print(self, e)
            raise e
        else:
            # try interpreting the key in the context of parent
            try:
                key_valid = self._parents(key)
            except Exception as e:
                print(self, e)
                raise e
        # if not key_valid:
        #     raise TypeError("Unexpected key type")

    def _point(self, key=None):
        """
            This is how Coordinates treats objects passed in the context of 'point' concept
        """
        if type(key) is list or type(key) is tuple :
            try:
                key_length = len(key)
            except Exception as e:
                # print(self, e)
                pass
            else:
                self.point = key
                return True

    def _parents(self, key=None):
        """
            This is how Coordinates treats objects passed in the context of 'parent' concept
        """
        # key is None
        # return own parents
        if key is None:
            return self._self_parents

        # key is of type Vertex
        # check if the Vertex is already a parent, if not then add as a parent
        if type(key) is Vertex:
            try:
                self._self_parents.add(key)
                # set coordinates of parent explicitly
                key._self_coordinates = self
            except Exception as e:
                print(self, e)
                raise e
            else:
                return self._self_parents

    def __str__(self):
        s = f'(Coordinates.\n' \
            + 'Value: ' + str(self.point) + ')'
        return s

    def __len__(self):
        try:
            own_dimension = len(self.point)
        except Exception as e:
            print(self, e)
            raise e
        return own_dimension

    def _scale(self, key=None):
        """
        Scale corrdinate using an iterable
        """
        try:
            own_dimension = len(self.point)
            key_dimension = len(key)
        except Exception as e:
            print(self, e)
            raise e
        for i in range(own_dimension):
            try:
                self.point[i] *= key[i]
            except Exception as e:
                print(self, e)
                raise e
        return self

    def _translate(self, key=None):
        """
        Translate corrdinate using an iterable
        """
        try:
            own_dimension = len(self.point)
            key_dimension = len(key)
        except Exception as e:
            print(str(e))
            raise e
        for i in range(own_dimension):
            try:
                self.point[i] += key[i]
            except Exception as e:
                print(str(e))
                raise e
        return self


class Vertex:
    def __init__(self, key=None):
        self.coordinates = self._coordinates  # Coordinates object(s) handling ('children')
        self._self_coordinates = None  # Actual self Coordinates
        self.sequence_number = None  # Return or set  3mf vertex sequence number

        self.parent_triangle = None  # Triangle object handling ('parent')

        # Try passing the key to self._coordinates
        try:
            assigned = self._coordinates(key)
        except Exception as e:
            print(self, e)
            raise e
        else:
            if not assigned:
                raise TypeError("Unexpected key type")

    def __str__(self):
        s = f'(Vertex.\n' \
            + 'Coordinate: ' + str(self.coordinates) + '\n'\
            + 'Sequence number: ' + str(self.sequence_number) + ')'
        return s

    def __len__(self):
        try:
            own_length = len(self._self_coordinates)
        except Exception as e:
            print(self, e)
            raise e
        return own_length

    def _coordinates(self, key=None):
        """
           Set or Get coordinates of this Vertex
           Also evaluate key for the __init__ method

           :param key: None, int, Coordinates object(s),
           :return: mainly own Coordinates,
        """

        # if key is None
        if key is None:
            if self._self_coordinates is not None:
                return self._self_coordinates
            else:
                return True

        # if key is Coordinates
        if type(key) is Coordinates:
            self._self_coordinates = key
            try:
                key.parents(self)
            except Exception as e:
                # print(self, e)
                pass
            return True

        # if argument parses to int
        # pass it to own Coordinates object
        v_idx = None
        try:
            v_idx = int(key)
        except Exception as e:
            pass
        if type(v_idx) is int:
            if self._self_coordinates is Coordinates:
                return self._self_coordinates(v_idx)

        # if argument is an iterable
        key_len = None
        try:
            key_len = len(key)
        except Exception as e:
            pass
        else:  # key is iterable
            # try constructing Coordinates using the key
            # and assigne it to self
            c = None
            try:
                c = Coordinates(key)
            except Exception as e:
                print(self, e)
                raise e
            else:
                if type(c) is Coordinates:
                    self._self_coordinates = c
                    return True

        raise TypeError("Unexpected key type")


class Triangle:
    """
    A Triangle is here, because it represents a part of the problem and a part of it's solution.

    As a part of the problem it represents an important concept in the domain of computer 3D graphics,
    and what I'm here for is kind of this very thing:
    to create a 3D surface (namely: the problem, the unknown thats being solved fot) for printing, using a computer.
        > So, 3D model are represented as a mesh of interconnected triangles.

    As a part of the solution it is a necessity for constructing a 3mf file, which is accepted by a slicer app
    (I chose 3mf because of how effortless it appeared to me to programatically built a 3d mesh
     while thinking of it in a rather familiar context of points and triangles in 3d space)
        > So, 3mf describes surfaces as interconnected triangles in a 3d space
    """
    def __init__(self, key=None):
        self.vertices = self._vertices  # Vertex object(s) handling ('children')
        self._self_v_0 = None  # Actual self vertex #0
        self._self_v_1 = None  # Actual self vertex #1
        self._self_v_2 = None  # Actual self vertex #2

        self.parent_triangle_mesh = None  # TriangleMesh object handling ('parent')

        self.flip = NotImplemented  # Return or set  self flipped

        # Try passing the key to self._vertices
        try:
            assigned = self._vertices(key)
        except Exception as e:
            print(self, e)
            raise e
        else:
            if not assigned:
                raise TypeError("Unexpected key type")

    def _vertices(self, key=None):
        """
        This is what triangle thinks of Vertices
        This explains what triangle would like to do with a Vertex, if if could recognise any

        :param key: None, int in range <0,3>, Vertex object(s)
        :return: mainly own vertices
        """

        # if argument is None
        # return the sequence of own vertices
        if key is None:
            return [self._self_v_0, self._self_v_1, self._self_v_2]
            # return self

        # if argument is Vertex object
        # # return
        if type(key) is Vertex:
            raise TypeError("The triangle does not know what to do with a single Vertex object")

        # if argument parses to int
        # return
        v_idx = None
        try:
            v_idx = int(key)
        except Exception as e:
            pass
        if type(v_idx) is int:
            if v_idx == 0:
                return self._self_v_0
            elif v_idx == 1:
                return self._self_v_1
            elif v_idx == 2:
                return self._self_v_2
            else:
                raise IndexError("Index value out of range")

        # if argument is an iterable of length 3
        key_len = None
        try:
            key_len = len(key)
        except Exception as e:
            pass
        else:
            if key_len is not None and key_len == 3:
                self._self_v_0 = key[0]
                self._self_v_1 = key[1]
                self._self_v_2 = key[2]
                # if a triangle is given 3 vertices, it adopts them
                if type(key[0]) is Vertex:
                    try:
                        key[0].parent_triangle = self
                    except Exception as e:
                        # print(self, e)
                        pass
                if type(key[1]) is Vertex:
                    try:
                        key[1].parent_triangle = self
                    except Exception as e:
                        # print(self, e)
                        pass
                if type(key[2]) is Vertex:
                    try:
                        key[2].parent_triangle = self
                    except Exception as e:
                        # print(self, e)
                        pass
                return True
            else:
                raise IndexError("Expected exactly 3 objects")

        raise TypeError("Unexpected key type")


# """ SELF TEST """
# if __name__ == "__main__":
#     # if loaded as __main__ run self test
#     subprocess.call(["python", "LightPicture_Test.py"])



v0 = Vertex()
c0 = Coordinates(v0)
r0 = c0.parents()
passed = v0 in r0



""" Potential classes below """

# class TriangleMesh:
#     def __init__(self, key=None):
#         self.triangles = NotImplemented  # Return or set iterable with Triangle objects
#         self.vertices = None  # Return iterable with all Vertex objects that belong Triangles that belong to the Mesh
#
#         self.addTriangles = None  # Add a Triangle object(s) to the mesh
#         self.removeTriangles = None  # Removes Triangle object(s) from the mesh
#
#


# class VertexSpace:
#     def __init__(self, key=None):
#         self.dimensions = None # Return space dimensions
#         self.vertex_space = None  # Return or set iterable with Vertex objects
#
#         self.vertexCount = None  # Returns the number of Vertex objects in the space
