""" VERSION INFO
    Current:
        v_4_5
            Added side walls generation
            Overall this is actually functional.
            Works tolerably for small files.

    History:
        v_4_4
            Vertex scaling - z scale working
            Pretty much working, seems usable in limited cases

            !!! still needs to add side walls
        v_4_3
            classes Vertex, Triangle and TriangleMesh moved to separate file named 'mesh.py'
            Implementing ImageConverter class
        v_4_2
            Tested TriangeMeshBuilder basic functionality, saving to 3mf file, timing
            * see test test_random_big_file for details of usage
        v_4_1
            Added TriangleMeshBuilder class
            Integrated TriangleMesh and 3mfFileWriter classes into the TriangleMeshBuilder

            !! see test_create_sample_file in unit test file
            !! for a quick reference and wirking example
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
import threading
import time
import random
import math
from mesh import *

class Xml3mfWriter:
    """
        this class is designed to format global vertices and triangels list from LightVoxelBox object
        and put them into the actual 3mf file and package
    """

    def __init__(self, triangle_mesh: TriangleMesh):
        self.triangle_mesh = triangle_mesh
        self.xml_root = None  # :ET.Element
        self.xml_vertices = None  # :ET.Element
        self.xml_triangles = None  # :ET.Element
        self._debug = False

    def mesh_to_xml(self):
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

        For the TriangleMeshBuilder you can provide a list of points in the form of [p_1, p_2, p_3, ...]
            where p_n is [x, y, z]
        it can eventually be used to save 3mf file
        it will take care of
            - creating a list of UNIQIE points (because every point WILL belong to more than one triangle)
            - putting them in unique order into a file
            - describing triangles using this ordering information i terms of defining vertices of the triangles
    """
    def __init__(self, size, scale):
        self.triangle_mesh = TriangleMesh()
        self.triangle = self._triangle  # add a triangle with given [[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]]

        self.writer = Xml3mfWriter(self.triangle_mesh)

        self.mesh_to_xml = self._mesh_to_xml
        self.save_3mf = self._save_3mf

        self._3d_space = None
        self._vertex = self.__vertex  # add or return vertex at given [x, y, z]

        # require key to be in format [x, y, z] - space dimensions
        # TODO: recongnize and valuate the key instead of just accepting it as 'size'
        self.size = size
        self.scale = scale

        # prepare the 3d space - it can actually take significant amount of time to just construct the array
        self._init_3d_space()

    def _init_3d_space(self):
        # This array is created so that the addressing is _3d_space[x][y][z]
        self._3d_space = \
            [[[None for z in range(self.size[2])] for y in range(self.size[1])] for x in range(self.size[0])]

    def __vertex(self, key: [] = None):
        """
            if there is a Vertex at given point then return it
            if there is no Vertex then create it and then return it
            Input argument should be [x, y, z]
        """
        # return Vertex at given coordinates, if there is any
        # print(key)
        try:
            this_vertex = self._3d_space[key[0]][key[1]][key[2]]
        except IndexError as e:
            print(key)
            raise e

        # print(key[0],key[1],key[2])
        if this_vertex is not None:
            return this_vertex

        # if there is None hten create it and then return it
        # TODO: IS THIS the right space to inherit voxel_size?????
        coords = [key[0]*self.scale[0], key[1]*self.scale[1], key[2]*self.scale[2]]

        # print('new vertex coords:', coords)
        this_vertex = Vertex(coords)
        this_vertex = Vertex(coords)
        self._3d_space[key[0]][key[1]][key[2]] = this_vertex
        return this_vertex

    def _triangle(self, key: [] = None):
        """
            check if all required vertices are existing, if not add necessary
            construct Triangle object

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

    def _mesh_to_xml(self):
        self.writer.mesh_to_xml()

    def _save_3mf(self):
        self.writer.save_3mf()


class ImageConverter:
    """
        This class should represent an object that can translate an 2d image into 3d mesh
        the output 3d mesh is defined as:
            list of points in the form of [p_1, p_2, p_3, ...]
                where each point p_n is [some_x, some_y, some_z]

        Note: the order of vertices inside a triangle is important, however it can be ignored at this point
              because slicer program will correct the orientation of individual triangles.
              What matters is that the triangles make up a closed, legal 3d shape.
    """

    def __init__(self, image: Image, scale):
        self._image = image  # input Image object (as seen in XY plane)
        self._image_size = image.size  # image dimensions
        self._pixels = image.load()  # initialize pixel-level access object
        self._height_map = None  # 2D array representing each image pixel 'height' (in Z direction)
        self._height_max = 0  # the highest value from height_map

        # TODO: this is static test - do something with it later - its used to initialize builder
        self.voxel_scale = scale  # [1, 1, 0.1]

        self._tmb = None  # a TriangleMeshBuilder object

        self.__init_height_map()
        self.__init_builder(self._image_size, self.voxel_scale)

    def __init_builder(self, image_size, voxel_scale):
        """
            Init function
        :param image_size:
        :param voxel_size:
        :return:
        """
        # init builder
        # dimensions are image_size * voxel size * 2
        # multiply by 2 required, because voxel of size [1,1,1] requires 2 points in each direction
        x_size = int(math.ceil(image_size[0])) * 2  # multiply by 2 cause voxel siz e 1 requires 2 points
        y_size = int(math.ceil(image_size[1])) * 2  # multiply by 2 cause voxel size 1 requires 2 points
        z_size = int(math.ceil(self._height_max))
        self._tmb = TriangleMeshBuilder([x_size, y_size, z_size], voxel_scale)

    def __init_height_map(self):
        """
            Convert input Image object into 2d array
            where value at [x][y] represent desired height in Z plane
        """
        # initialize new, empty height_map array
        self._height_map = []
        # get image size
        size = self._image.size

        for x in range(size[0]):
            self._height_map.append([])
            for y in range(size[1]):
                # TODO: for now only take R channel: consider calculating average
                pixel_shade = self._pixels[x, y][0]
                # actual height is the 'reverse' of pixel shade - the thicker the mesh the darker it will look
                pixel_height = 255 - pixel_shade
                # avoid 0 thickness
                if pixel_height <= 0:
                    pixel_height = 4
                if pixel_height >= 255:
                    pixel_height = 254
                self._height_map[x].append(pixel_height)
                # keep updating max height
                if pixel_height > self._height_max:
                    self._height_max = pixel_height + 1  # this +1 seems crucial :D... just kidding, I know why

    def __get_voxel_tops(self, coords):
        """
        :param coords: [x, y] corresponding to height_map
        :param voxel_size: [sx, sy, sz] virtual voxel size around the point at coordinates
        :return: four points tha define this 'imaginaxy voxel's' top wall
        """
        # current height above XY base plane

        current_z = self._height_map[coords[0]][coords[1]]
        # top four points of this 'voxels pile'
        p00 = [
            coords[0] + 0,
            coords[1] + 0,
            current_z
        ]
        p10 = [
            coords[0] + 1,
            coords[1] + 0,
            current_z
        ]
        p11 = [
            coords[0] + 1,
            coords[1] + 1,
            current_z
        ]
        p01 = [
            coords[0] + 0,
            coords[1] + 1,
            current_z
        ]
        return {'p00': p00, 'p10': p10, 'p11': p11, 'p01': p01}

    def _construct_mesh(self):
        """
            This function can construct a triangles list from height map
        :param voxel_size: [x_ssize, y_size, z_size] - 'voxel dimensions' for calculating actual points
        :return:
        """
        pass

        # build XY base (bottom)
        # # simple rectangle as the bottom face of the mesh - just scale image dimensions accordingly
        # # first corner: (0, 0)
        # # width:: (image_width * voxel_size_x)
        # # height: (image_height * voxel_size_y)
        p00 = [
            0,
            0,
            0
        ]
        p10 = [
            self._image_size[0],
            0,
            0
        ]
        p11 = [
            self._image_size[0],
            self._image_size[1],
            0
        ]
        p01 = [
            0,
            self._image_size[1],
            0
        ]
        # give bottom face triangles to the builder
        self._tmb.triangle([p00, p10, p11])
        self._tmb.triangle([p00, p11, p01])

        # 'pass' through all pixels in map_height
        for pixel_x in range(self._image_size[0]):
            for pixel_y in range(self._image_size[1]):
                # # get 'voxel top wall' coordinates, like points on 'top' of the mesh
                tops = self.__get_voxel_tops([pixel_x, pixel_y])
                my_height = tops['p00'][2]  # just grab z of any point - theyre all on the same height
                # heights of neighbouring piles
                if pixel_x-1 < 0:
                    height_left = 0
                else:
                    height_left = self._height_map[pixel_x-1][pixel_y]
                if pixel_x+1 >= self._image_size[0]:
                    height_right = 0
                else:
                    height_right = self._height_map[pixel_x+1][pixel_y]
                if pixel_y-1 < 0:
                    height_front = 0
                else:
                    height_front = self._height_map[pixel_x][pixel_y-1]
                if pixel_y+1 >= self._image_size[1]:
                    height_back = 0
                else:
                    height_back = self._height_map[pixel_x][pixel_y+1]

                # # now ive got top point of this voxel
                # # iv also got heights of its 4 neighbours
                # # lets build the 'pile'

                # build the top face of current 'voxel'
                # print(tops)
                self._tmb.triangle([tops['p00'], tops['p10'], tops['p11']])
                self._tmb.triangle([tops['p00'], tops['p11'], tops['p01']])

                # # every pile may need to generate some walls around it
                # if its the lowest between its 4 neighbours, then no walls neded here
                # if its higher than particular neighbour then build wall between them
                #    which is: build wall between my two points and lower 2 points on the same vertical plane

                # check left side
                if height_left < my_height:
                    # need to build a wall
                    pu0 = [
                        tops['p00'][0],
                        tops['p00'][1],
                        tops['p00'][2]
                    ]
                    pu1 = [
                        tops['p01'][0],
                        tops['p01'][1],
                        tops['p01'][2]
                    ]
                    pd0 = [
                        tops['p00'][0],
                        tops['p00'][1],
                        height_left
                    ]
                    pd1 = [
                        tops['p01'][0],
                        tops['p01'][1],
                        height_left
                    ]
                    points = [pu0, pu1, pd0, pd1]
                    # print(tops)
                    # print(points)
                    self._tmb.triangle([points[0], points[1], points[2]])
                    self._tmb.triangle([points[1], points[2], points[3]])

                # check right side
                if height_right < my_height:
                    # need to build a wall
                    pu0 = [
                        tops['p10'][0],
                        tops['p10'][1],
                        tops['p10'][2]
                    ]
                    pu1 = [
                        tops['p11'][0],
                        tops['p11'][1],
                        tops['p11'][2]
                    ]
                    pd0 = [
                        tops['p10'][0],
                        tops['p10'][1],
                        height_right
                    ]
                    pd1 = [
                        tops['p11'][0],
                        tops['p11'][1],
                        height_right
                    ]
                    points = [pu0, pu1, pd0, pd1]
                    # print(tops)
                    # print(points)
                    self._tmb.triangle([points[0], points[1], points[2]])
                    self._tmb.triangle([points[1], points[2], points[3]])

                # check front side
                if height_front < my_height:
                    # need to build a wall
                    pu0 = [
                        tops['p00'][0],
                        tops['p00'][1],
                        tops['p00'][2]
                    ]
                    pu1 = [
                        tops['p10'][0],
                        tops['p10'][1],
                        tops['p10'][2]
                    ]
                    pd0 = [
                        tops['p00'][0],
                        tops['p00'][1],
                        height_front
                    ]
                    pd1 = [
                        tops['p10'][0],
                        tops['p10'][1],
                        height_front
                    ]
                    points = [pu0, pu1, pd0, pd1]
                    # print(tops)
                    # print(points)
                    self._tmb.triangle([points[0], points[1], points[2]])
                    self._tmb.triangle([points[1], points[2], points[3]])

                # check back side
                if height_back < my_height:
                    # need to build a wall
                    pu0 = [
                        tops['p01'][0],
                        tops['p01'][1],
                        tops['p01'][2]
                    ]
                    pu1 = [
                        tops['p11'][0],
                        tops['p11'][1],
                        tops['p11'][2]
                    ]
                    pd0 = [
                        tops['p01'][0],
                        tops['p01'][1],
                        height_back
                    ]
                    pd1 = [
                        tops['p11'][0],
                        tops['p11'][1],
                        height_back
                    ]
                    points = [pu0, pu1, pd0, pd1]
                    # print(tops)
                    # print(points)
                    self._tmb.triangle([points[0], points[1], points[2]])
                    self._tmb.triangle([points[1], points[2], points[3]])

    def save_3mf(self):
        self._tmb._mesh_to_xml()
        self._tmb._save_3mf()




# load and calculate image
image = Image.open('sample_image_4.bmp')
t0 = time.perf_counter()
ic = ImageConverter(image, [1, 1, 0.03])
t0 = time.perf_counter() - t0

t1 = time.perf_counter()
ic._construct_mesh()
t1 = time.perf_counter() - t1


# build xml structure
t3 = time.perf_counter()
ic.save_3mf()
t3 = time.perf_counter() - t3

print('Init time:   ', t0)
print('Construction time: ', t1)
print('Save time:         ', t3)



#
# # working dimensions and triangle sarray
# [x, y, z] = [400, 400, 100]
# triangles = []
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
