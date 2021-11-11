""" VERSION INFO
    Current:
        v_4_1
            Added TriangleMeshBuilder class
            Integrated TriangleMesh and 3mfFileWriter classes into the TriangleMeshBuilder

            !! see test_create_sample_file in unit test file
            !! for a quick reference and wirking example

    History:
        v_3_3
            Working on Triangle Mesh, added 3mffilewriter class
        v_3_2
            Merged Vertex and Coordinate classes together
"""

from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil
import timeit
import subprocess


class Vertex:
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


class Xml3mfWriter:
    """ this class is designed to format global vertices and triangels list from LightVoxelBox object """
    """ and put them into the actual 3mf file and package """

    def __init__(self, triangle_mesh: TriangleMesh):
        self.triangle_mesh = triangle_mesh
        self.xml_root = None  # :ET.Element
        self.xml_vertices = None  # :ET.Element
        self.xml_triangles = None  # :ET.Element
        self._debug = False

    def write_triangle_mesh(self):
        self.create_3mf_structure()
        global_vertex_number = 0
        triangles = self.triangle_mesh.triangles()
        for t in triangles:
            # print(t)
            vertices = t.vertices()
            # for every vertex in triangle try appending to file and numbering it
            for v in vertices:
                # print('    ', v.coordinates())
                # get every Vertex in every Triangle

                # if Vertex has sequence number assigned then pass
                if v.sequence_number is not None:
                    continue

                # #if vertex has no sequence number - generate it, add vertex to file
                # assign current gvl and increase it by one
                v.sequence_number = global_vertex_number
                global_vertex_number += 1
                # add to xml structure
                # elements will be printed to file in the same order,
                # so adding them and numbering here at the same time keeps coherence
                new_vert = ET.SubElement(self.xml_vertices, 'vertex' )
                coord = v.coordinates()
                new_vert.attrib['x'] = str(coord[0])
                new_vert.attrib['y'] = str(coord[1])
                new_vert.attrib['z'] = str(coord[2])
                # print(str(new_vert))

            # now get the triangle itself and append to file
            new_tria = ET.SubElement(self.xml_triangles, 'triangle')
            new_tria.attrib['v1'] = str(vertices[0].sequence_number)
            new_tria.attrib['v2'] = str(vertices[1].sequence_number)
            new_tria.attrib['v3'] = str(vertices[2].sequence_number)

        self.save_3mf()

    def create_3mf_structure(self):
        """ Create basic structure of 3mf file (without actual vertices and triangles) """
        # main xml element - "model". XML Root element.
        self.xml_root = ET.Element('model')
        self.xml_root.attrib['unit'] = 'millimeter'

        # # 3mf "resources" element:
        # xml element - "model" -> "resources"
        mf_resources = ET.SubElement(self.xml_root, 'resources')

        # xml element - "model" -> "resources" -> "object"
        mf_object = ET.SubElement(mf_resources, 'object')
        mf_object.attrib['type'] = 'model'
        mf_object.attrib['id'] = '1'
        # xml element - "model" -> "resources" -> "object" -> "mesh"
        # this will contain ACTUAL 3d object data: vertices and triangles
        mf_mesh = ET.SubElement(mf_object, 'mesh')
        # xml element - "model" -> "resources" -> "object" -> "mesh" -> "vertices"
        self.xml_vertices = ET.SubElement(mf_mesh, 'vertices')
        # xml element - "model" -> "resources" -> "object" -> "mesh" -> "triangles"
        self.xml_triangles = ET.SubElement(mf_mesh, 'triangles')

        # xml element - "model" -> "resources" -> "object"
        mf_object = ET.SubElement(mf_resources, 'object')
        mf_object.attrib['type'] = 'model'
        mf_object.attrib['id'] = '2'
        # xml element - "model" -> "resources" -> "object" -> "mesh" -> "components"
        mf_components = ET.SubElement(mf_object, 'components')

        # # create more components (copy of object) and translate them
        mf_component = ET.SubElement(mf_components, 'component')
        mf_component.attrib['objectid'] = '1'

        # # 3mf "build" element:
        # xml element - "model" -> "build": this will reference just a single 3D based on "resources"
        mf_build = ET.SubElement(self.xml_root, 'build')
        # xml element - "model" -> "build" -> "item"
        mf_item = ET.SubElement(mf_build, 'item')
        mf_item.attrib['objectid'] = '2'

        if self._debug:
            print('Basic xml structure of 3mf file created.')

    def fill_xml_vertices(self):
        for v in self.voxel_box.global_vertices:
            new_vert = ET.SubElement(self.xml_vertices, 'vertex')
            new_vert.attrib['x'] = str(v[0][0])
            new_vert.attrib['y'] = str(v[0][1])
            new_vert.attrib['z'] = str(v[0][2])
        # if self._debug:
        #     print(v[0][0], v[0][1], v[0][2])
        if self._debug:
            print(f'{len(self.voxel_box.global_vertices)} vertex elements created.')

    def fill_xml_triangles(self):
        for t in self.voxel_box.global_triangles:
            new_tria = ET.SubElement(self.xml_triangles, 'triangle')
            new_tria.attrib['v1'] = str(t[0])
            new_tria.attrib['v2'] = str(t[1])
            new_tria.attrib['v3'] = str(t[2])
        if self._debug:
            print(f'{len(self.voxel_box.global_triangles)} triangle elements created.')

    def save_3mf(self):
        """ Save complete 3mf xml structure to a file and make it a legit 3mf package  """
        # create folder named "3D"
        try:
            os.mkdir('ZIP')
            os.mkdir('ZIP/3D')
        except FileExistsError:
            pass
        # make xml pretty and save xml file as "[name].model"
        xmlstr = minidom.parseString(ET.tostring(self.xml_root)).toprettyxml(indent="   ")
        with open("ZIP/3D/mymesh.model", "w") as f:
            f.write(xmlstr)

        # compress "3D" folder to a zip file
        shutil.make_archive('mymesh', 'zip', 'ZIP')

        # delete previous 3mf file is exists
        if os.path.isfile('mymesh.3mf'):
            os.remove('mymesh.3mf')
        # change file extension from 'zip' to '3mf'
        try:
            os.rename('mymesh.zip', 'mymesh.3mf')
        except FileExistsError as e:
            print(str(e))

        if self._debug:
            print('3mf package created.')


class TriangleMeshBuilder:
    """
        This class describes an object that connects abstract points in space with Triangel objects
        while making sure that no Vertex object is unnecessary duplicated.

        Basicaly it will hold a 3d array of Vertex objects
        It can return a Vertexe at given coordinates
        it can abstract Triangle construction

        methods:
            add vertex
                if there is a Vertex at given point then return it
                if there is no Vertex then create it and then return it
            add triangle
                check if all required vertices are existing, if not add necessary
                construct Triangle object

    """
    def __init__(self, key=None):
        self.size = [200, 200, 200]

        self.triangle_mesh = TriangleMesh()
        self.triangle = self._triangle  # add a triangle with given [[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]]

        self.write_3mf_file = self._write_3mf_file

        self._3d_space = None
        self._vertex = self.__vertex  # add or return vertex at given [x, y, z]

        # require key to be in format [x, y, z] - space dimensions
        self.size = key

        self._init_3d_space()


    def _init_3d_space(self):
        # This array is created so that the addressing is _3d_space[x][y][z]
        self._3d_space = \
            [[[None for x in range(self.size[0])] for y in range(self.size[1])] for z in range(self.size[2])]

    def __vertex(self, key: [] = None):
        """
        Input argument should be [x, y, z]
        """
        # return Vertex at given coordinates, if there is any
        this_vertex = self._3d_space[key[0]][key[1]][key[2]]
        if this_vertex is not None:
            return this_vertex

        # if there is None hten create it and then return it
        coords = [key[0], key[1], key[2]]
        # print('new vertex coords:', coords)
        this_vertex = Vertex(coords)
        self._3d_space[key[0]][key[1]][key[2]] = this_vertex
        return this_vertex

    def _triangle(self, key: [] = None):
        """
            Input argument should be [[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]]
        """
        # extract 3 disctinct points
        v0_coords = key[0]
        v1_coords = key[1]
        v2_coords = key[2]

        # get Vertex objects via own method
        v0 = self.__vertex(v0_coords)
        v1 = self.__vertex(v1_coords)
        v2 = self.__vertex(v2_coords)

        # construct a Triangle and return it
        t = Triangle([v0, v1, v2])
        self.triangle_mesh.triangles(t)
        return t

    def _write_3mf_file(self):
        # create 3mf writer
        writer = Xml3mfWriter(self.triangle_mesh)
        # give the created mesh to the writer
        writer.write_triangle_mesh()




# """ SELF TEST """
# if __name__ == "__main__":
#     # if loaded as __main__ run self test
#     subprocess.call(["python", "LightPicture_Test.py"])



# v0 = Vertex()
# c0 = Coordinates(v0)
# r0 = c0.parents()
# passed = v0 in r0
#
#
# print('Build finished')

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
