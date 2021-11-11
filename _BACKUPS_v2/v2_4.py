"""

# # classes to represent actual 3d space
# # last step between 3mf file structure and the rest of the program
# # it should be easy to translate information from these structures to 3mf format
#
# class Vertex
#     parent_space : PointSpace    # a space the point belongs to
#     x, y, z    # own coordinates in parent space
#     global_vertex_number    # 3mf structure vertex sequence number
#
# class Triangle
#     v1, v2, v3 : Vertex    # 3 vertices that form this triangle
#
# class Space
#     x_size, y_size_, z_size    # space dimensions
#     vertex_space[][][] : Vertex    # 3d array of Vertex, for structured storage
#
#

STATUS: triangle class tested with single-object interface

"""

from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil
import timeit


class Coordinates:
    """
    Abstract coordinate vector
    """

    def __init__(self, key=None):
        self.coordinates = None  # Return or set a set of numbers

        self.parent_vertex = None  # Return or set parent Vertex

        self.scale = self._scale  # Return scaled Coordinate
        self.translate = self._translate  # Return translated Coordinate e

        if key is not None:
            try:
                _ = len(key)
            except Exception as e:
                print(e)
                raise e
            self.coordinate = key

    def __str__(self):
        s = f'(Coordinate Object.\n' \
            + 'Value: ' + str(self.coordinate) + ')'
        return s

    def __len__(self):
        try:
            own_dimension = len(self.coordinate)
        except Exception as e:
            print(e)
            raise e
        return own_dimension

    def _scale(self, key=None):
        """
        Scale corrdinate using an iterable
        """
        try:
            own_dimension = len(self.coordinate)
            key_dimension = len(key)
        except Exception as e:
            print(str(e))
            raise e
        for i in range(own_dimension):
            try:
                self.coordinate[i] *= key[i]
            except Exception as e:
                print(str(e))
                raise e
        return self

    def _translate(self, key=None):
        """
        Translate corrdinate using an iterable
        """
        try:
            own_dimension = len(self.coordinate)
            key_dimension = len(key)
        except Exception as e:
            print(str(e))
            raise e
        for i in range(own_dimension):
            try:
                self.coordinate[i] += key[i]
            except Exception as e:
                print(str(e))
                raise e
        return self


class Vertex:
    def __init__(self, coordinates=None, sequence_number=None, parent_triangle=None):
        self.coordinates = self._coordinates  # Coordinates function
        self._self_coordinates = None  # Actual self Coordinates
        self.sequence_number = sequence_number  # Return or set  3mf vertex sequence number

        self.parent_triangle = None  # preferably a parent Triangle object

        if type(coordinates) is Coordinates:
            self.coordinates = coordinates

        if type(parent_triangle) is Triangle:
            self.parent_triangle = parent_triangle
            self.parent_triangle_mesh = parent_triangle.parent_triangle_mesh

    def __str__(self):
        s = f'(Vertex Object.\n' \
            + 'Coordinate: ' + str(self.coordinates) + '\n' \
            + 'Vertex number: ' + str(self.sequence_number) + ')'
        return s

    def __len__(self):
        try:
            own_length = len(self.coordinate)
        except Exception as e:
            print(e)
            raise e
        return own_length

    def _coordinates(self, key=None):
        """
           Set or Get coordinates of this Vertex
           Also evaluate key for the __init__ method

           :param key: None, int, object of type Coordinates, 
           :return: mainly own Coordinates
        """

        # if argument is None
        if key is None:
            return self._self_coordinates

        # if argument parses to int
        # try evaluating it with own Coordinates
        v_idx = None
        try:
            v_idx = int(key)
        except Exception as e:
            pass
        if v_idx is not None:
            self._self_coordinates()
            raise IndexError("Index value out of range")

        # if argument is an iterable of length 3
        key_len = None
        try:
            key_len = len(key)
        except Exception as e:
            pass
        else:
            if key_len is not None and key_len == 3:
                self._v_0 = key[0]
                self._v_1 = key[1]
                self._v_2 = key[2]
                if type(key[0]) is Vertex:
                    try:
                        key[0].parent_triangle = self
                    except Exception as e:
                        print(e)
                        pass
                if type(key[1]) is Vertex:
                    try:
                        key[1].parent_triangle = self
                    except Exception as e:
                        print(e)
                        pass
                if type(key[2]) is Vertex:
                    try:
                        key[2].parent_triangle = self
                    except Exception as e:
                        print(e)
                        pass
                return True
            else:
                raise IndexError("Expected exactly 3 objects")

        raise TypeError("Unexpected key type")


class Triangle:
    def __init__(self, key=None):
        self.vertices = self._vertices  # vertices function
        self._self_v_0 = None  # Actual self vertex #0
        self._self_v_1 = None  # Actual self vertex #1
        self._self_v_2 = None  # Actual self vertex #2

        self.parent_triangle_mesh = None  # Return or set  parent TriangleMesh

        self.flip = NotImplemented  # Return or set  self flipped

        # Try passing the key to self._vertices
        try:
            assigned = self._vertices(key)
        except Exception as e:
            print(e)
        else:
            if not assigned:
                raise TypeError("Unexpected key type")

    def _vertices(self, key=None):
        """
        Set or Get vertices of this Triangle
        Also evaluate key for the __init__ method

        :param key: None, int in range <0,3>, iterable of len=3
        :return: mainly own vertices
        """

        # if argument is None
        if key is None:
            return [self._self_v_0, self._self_v_1, self._self_v_2]

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
                if type(key[0]) is Vertex:
                    try:
                        key[0].parent_triangle = self
                    except Exception as e:
                        print(e)
                        pass
                if type(key[1]) is Vertex:
                    try:
                        key[1].parent_triangle = self
                    except Exception as e:
                        print(e)
                        pass
                if type(key[2]) is Vertex:
                    try:
                        key[2].parent_triangle = self
                    except Exception as e:
                        print(e)
                        pass
                return True
            else:
                raise IndexError("Expected exactly 3 objects")

        raise TypeError("Unexpected key type")


class TriangleMesh:
    def __init__(self, key=None):
        self.triangles = NotImplemented  # Return or set iterable with Triangle objects
        self.vertices = None  # Return iterable with all Vertex objects that belong Triangles that belong to the Mesh

        self.addTriangles = None  # Add a Triangle object(s) to the mesh
        self.removeTriangles = None  # Removes Triangle object(s) from the mesh


# class VertexSpace:
#     def __init__(self, key=None):
#         self.dimensions = None # Return space dimensions
#         self.vertex_space = None  # Return or set iterable with Vertex objects
#
#         self.vertexCount = None  # Returns the number of Vertex objects in the space


# c0 = Coordinate([1,2])
# v0 = Vertex(c0, 0)
# c1 = Coordinate([1,2])
# v1 = Vertex(c1, 0)
# c2 = Coordinate([1,2])
# v2 = Vertex(c2, 0)
#
# t = Triangle([v0, v1, v2])


c0 = Coordinates([0, 0])
v0 = Vertex(sequence_number=0)
v0.coordinate = c0

c1 = Coordinates()
c1 = Coordinates([1, 11])
v1 = Vertex(c1, 0)

c2 = Coordinates([2, 22])
v2 = Vertex(c2, 0)

t = Triangle([v0, v1, v2])
print(t.vertices())
print(t.vertices(1))
print(t.vertices([v2, v1, v0]))





