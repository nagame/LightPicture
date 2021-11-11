
from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil
import timeit
import subprocess
import threading
import time
import random


class Vertex:
    """
    This class represents the idea of Vertex.

    in 3d graphics context:
        Vertex i s point defined in 3d space
    in 3mf context:
        also has additional 'sequence number' assigned. This is it's place on the 3mf vertices list.
    """
    def __init__(self, key=None):
        self.coordinates = self._coordinates  # Interpret key in 'coordinates' context
        self._self_coordinates = []  # Actual self Coordinates
        self.sequence_number = None  # Return or set  3mf vertex sequence number

        self.parents = self._parents  # Interpret key in 'parent' context
        self._self_parents = set()

        self.scale = self._scale  # Return scaled Coordinate
        self.translate = self._translate  # Return translated Coordinate e

        # Try passing key in coordinates context
        try:
            assigned = self._coordinates(key)
        except Exception as e:
            print(self, e)
            raise e
        # if key not evaluated then try in parents context
        if not assigned:
            try:
                assigned = self._parents(key)
            except Exception as e:
                print(self, e)
                raise e

    def _parents(self, key=None):
        """
           This is how Vertex treats objects passed in the context of 'parent' concept
        """
        # key is None
        # return own parents
        if key is None:
            return self._self_parents

        # key is of type Triangle
        # check if the Triangle is already a parent, if not then add as a parent
        if type(key) is Triangle:
            try:
                self._self_parents.add(key)
            except Exception as e:
                print(self, e)
                raise e
            else:
                return self._self_parents

    def _coordinates(self, key=None):
        """
           Set or Get coordinates of this Vertex
           Also evaluate key for the __init__ method

           :param key: None, int, iterable of 3 ints
           :return: mainly own Coordinates,
        """

        # if key is None
        if key is None:
            if self._self_coordinates is not None:
                return self._self_coordinates
            else:
                return True

        # if key is iterable of 3 ints
        key_len = None
        try:
            key_len = len(key)
        except Exception as e:
            pass
        else:  # key is iterable
            # assign to own coordinates
            if type(key_len) is int and key_len == 3:
                for c in key:
                    if type(c) is not float and type(c) is not int:
                        raise TypeError("Expected exactly 3 numbers")
                self._self_coordinates = key
                return True
            else:
                return False

        # if argument parses to int
        # pass it to own Coordinates object
        v_idx = None
        try:
            v_idx = int(key)
        except Exception as e:
            pass
        if type(v_idx) is int:
            if -3 < v_idx < 3:
                return self._self_coordinates[v_idx]

        return False

    def _scale(self, key=None):
        """
        Scale corrdinate using an iterable
        """
        try:
            own_dimension = len(self._self_coordinates)
            key_dimension = len(key)
        except Exception as e:
            print(self, e)
            raise e
        for i in range(own_dimension):
            try:
                self._self_coordinates[i] *= key[i]
            except Exception as e:
                print(self, e)
                raise e
        return self

    def _translate(self, key=None):
        """
        Translate corrdinate using an iterable
        """
        try:
            own_dimension = len(self._self_coordinates)
            key_dimension = len(key)
        except Exception as e:
            print(str(e))
            raise e
        for i in range(own_dimension):
            try:
                self._self_coordinates[i] += key[i]
            except Exception as e:
                print(str(e))
                raise e
        return self

    def __str__(self):
        s = f'(Vertex.\n' \
            + 'Coordinate: ' + str(self.coordinates) + '\n' \
            + 'Sequence number: ' + str(self.sequence_number) + ')'
        return s

    def __len__(self):
        try:
            own_length = len(self._self_coordinates)
        except Exception as e:
            print(self, e)
            raise e
        return own_length


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

        self.parent_mesh = self._parent_mesh  # TriangleMesh object handling ('parent')
        self._self_parent_mesh = None

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
                # key is iterable of length 3
                if type(key[0]) is Vertex and \
                        type(key[1]) is Vertex and \
                        type(key[2]) is Vertex:
                    # if a triangle is given 3 vertices, it adopts them
                    try:
                        key[0].parent_triangle = self
                        key[1].parent_triangle = self
                        key[2].parent_triangle = self
                    except Exception as e:
                        # print(self, e)
                        pass
                    self._self_v_0 = key[0]
                    self._self_v_1 = key[1]
                    self._self_v_2 = key[2]
                    return True
                elif type(key[0]) is not int and \
                        type(key[1]) is not int and \
                        type(key[2]) is not int:
                    # if iterable content is not Vertex and not int objects  then try to construct Vertex(s)
                    try:
                        self._self_v_0 = Vertex(key[0])
                        self._self_v_1 = Vertex(key[1])
                        self._self_v_2 = Vertex(key[2])

                        key[0].parent_triangle = self
                        key[1].parent_triangle = self
                        key[2].parent_triangle = self
                    except:
                        pass
                    return True
                else:
                    self._self_v_0 = key[0]
                    self._self_v_1 = key[1]
                    self._self_v_2 = key[2]
                return True
            else:
                raise IndexError("Expected exactly 3 objects")

        raise TypeError("Unexpected key type")

    def _parent_mesh(self, key=None):
        """
            This is how Triangle treats objects passed in the context of 'parent' concept
        """
        if key is None:
            # is key is none just return self parent
            return self._self_parent_mesh

        if type(key) is TriangleMesh:
            # if key is type Triangle then assign it as self parent
            self._self_parent_mesh = key


class TriangleMesh:
    """
        This is a container class for Triangles
    """
    def __init__(self, key=None):
        self.triangles = self._triangles  # Evaluate key in triangle context
        self._self_triangles = []  # Actual triangles

        # Try passing the key to self._vertices
        try:
            evaluated = self._triangles(key)
        except Exception as e:
            print(self, e)
            raise e
        else:
            pass
            # # no easy tool at hand to still recognize exception here

    def _triangles(self, key=None):
        """
           This is how Vertex treats objects passed in the context of 'parent' concept
        """
        if key is None:
            return self._self_triangles

        if type(key) is Triangle:
            # if key is Triangle add it to own triangles
            self._self_triangles.append(key)
            return True

        # if key is iterable try adding elements as Triangles
        key_len = None
        try:
            key_len = len(key)
        except Exception as e:
            # print(e)
            pass
        if type(key_len) is int:
            for k in key:
                if type(k) is Triangle:
                    self._self_triangles.append(k)
            return True

        return False

