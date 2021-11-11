""" This is more or less ready, but take sucha a long time to minimize and name vertices...
 10x10x10 voxel space take like tens of seconds..."""


from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil


# initial definition of LightVoxelBox class for reference
class LightVoxelBox:
    def __init__(self):
        self.voxel_space = None
        self._debug = True


# initial definition of LightVoxel class for reference
class LightVoxel:
    def __init__(self):
        self._debug = True


# =====================================================================================================================


# extended definition of LightVoxel class
class LightVoxel:
    """ this class represents a single, abstract voxel ('3D-pixel') """
    """ and is intended to be used by LightVoxelBox """

    def __init__(self, x, y, z, parent: LightVoxelBox):
        [self._x, self._y, self._z] = [x, y, z]
        self._parent_box = parent
        self._debug = False
        self.invisible = None
        self.neighbours = {
            "front": None,
            "back": None,
            "left": None,
            "right": None,
            "top": None,
            "bottom": None,
            # 'others' ar all neighbours not sharing a whole face - only single edge or vertex
            "others": [None, None, None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, None, None]
        }
        self.visible_faces = {
            "front": None,
            "back": None,
            "left": None,
            "right": None,
            "top": None,
            "bottom": None,
        }
        self.unit_vertices = [
            [
                [
                    ['x0', 'y0', 'z0', {'global_vertex_number': None}],
                    ['x0', 'y0', 'z1', {'global_vertex_number': None}]
                ],
                [
                    ['x0', 'y1', 'z0', {'global_vertex_number': None}],
                    ['x0', 'y1', 'z1', {'global_vertex_number': None}]
                ]
            ],
            [
                [
                    ['x1', 'y0', 'z0', {'global_vertex_number': None}],
                    ['x1', 'y0', 'z1', {'global_vertex_number': None}]
                ],
                [
                    ['x1', 'y1', 'z0', {'global_vertex_number': None}],
                    ['x1', 'y1', 'z1', {'global_vertex_number': None}]
                ]
            ]
        ]
        self._coord_to_vertex = {
            (0, 0, 0): 0,
            (0, 0, 1): 1,
            (0, 1, 0): 2,
            (0, 1, 1): 3,
            (1, 0, 0): 4,
            (1, 0, 1): 5,
            (1, 1, 0): 6,
            (1, 1, 1): 7
        }
        self._vertex_to_coord = {
            0: (0, 0, 0),
            1: (0, 0, 1),
            2: (0, 1, 0),
            3: (0, 1, 1),
            4: (1, 0, 0),
            5: (1, 0, 1),
            6: (1, 1, 0),
            7: (1, 1, 1)
        }
        self._face_names = {'front': 0, 'back': 1, 'top': 2, 'bottom': 3, 'left': 4, 'right': 5}
        self._face_to_local_triangles = {
            'front':  ((0, 4, 1), (4, 5, 1)),
            'back':   ((3, 7, 2), (6, 2, 7)),
            'top':    ((1, 5, 3), (5, 7, 3)),
            'bottom': ((0, 2, 6), (0, 6, 4)),
            'left':   ((1, 2, 0), (1, 3, 2)),
            'right':  ((4, 6, 5), (6, 7, 5))
        }

    def check_invisible(self):
        """ Evaluate if self is invisible """
        """ that is: check if all sides covered by other voxels """

        # Set invisible to True, we will check  all cases that could change this.
        # May return immediately after changing self.invisible to False
        self.invisible = True

        # Check if self has any coordinate equal to 0, if so then the voxel will be visible
        # (this has to be checked separately because array[-1] does not yield exception)
        if self._x == 0 or self._y == 0 or self._z == 0:
            self.invisible = False
            return

        # # Now check if any neighbouring voxel is None or outside the voxel_space
        # # if so then the voxel will be visible

        # check if any neighbour outside voxel_space range
        neighbours = []
        # Get all relevant neighbouring voxels
        try:
            neighbours = [
                self._parent_box.voxel_space[self._x - 1][self._y][self._z],
                self._parent_box.voxel_space[self._x + 1][self._y][self._z],
                self._parent_box.voxel_space[self._x][self._y - 1][self._z],
                self._parent_box.voxel_space[self._x][self._y + 1][self._z],
                self._parent_box.voxel_space[self._x][self._y][self._z - 1],
                self._parent_box.voxel_space[self._x][self._y][self._z + 1]
            ]
        except IndexError:
            # if self is at a boundary of voxel_space then self is not invisible
            self.invisible = False

        # if any of them is None ('empty') then the voxel will be visible
        for n in neighbours:
            if n is None:
                self.invisible = False

    def find_neighbours(self):
        # fill the self.neighbours array
        # this may be called only after invoking create_volume_voxels of LightVoxelBox
        try:
            if self._x > 0:
                self.neighbours['left'] = self._parent_box.voxel_space[self._x - 1][self._y][self._z]  # left
        except IndexError:
            pass
        try:
            self.neighbours['right'] = self._parent_box.voxel_space[self._x + 1][self._y][self._z]  # right
        except IndexError:
            pass
        try:
            if self._y > 0:
                self.neighbours['front'] = self._parent_box.voxel_space[self._x][self._y - 1][self._z]  # front
        except IndexError:
            pass
        try:
            self.neighbours['back'] = self._parent_box.voxel_space[self._x][self._y + 1][self._z]  # back
        except IndexError:
            pass
        try:
            if self._z > 0:
                self.neighbours['bottom'] = self._parent_box.voxel_space[self._x][self._y][self._z - 1]  # bottom
        except IndexError:
            pass
        try:
            self.neighbours['top'] = self._parent_box.voxel_space[self._x][self._y][self._z + 1]  # top
        except IndexError:
            pass

    def calculate_visible_faces(self):
        # calculate and save which faces of self are gonna be visible

        # this function is designed to be called only after invoking
        # create_volume_voxels() and then mark_invisible_voxels()
        # from LightVoxelBox object

        # no visible faces if voxel marked invisible as a whole
        if self.invisible:
            return

        # # now, all faces will be visible on self, except these that have neighbour
        # left
        if type(self.neighbours['left']) is LightVoxel:
            self.visible_faces['left'] = False
        else:
            self.visible_faces['left'] = True
        # right
        if type(self.neighbours['right']) is LightVoxel:
            self.visible_faces['right'] = False
        else:
            self.visible_faces['right'] = True
        # front
        if type(self.neighbours['front']) is LightVoxel:
            self.visible_faces['front'] = False
        else:
            self.visible_faces['front'] = True
        # back
        if type(self.neighbours['back']) is LightVoxel:
            self.visible_faces['back'] = False
        else:
            self.visible_faces['back'] = True
        # bottom
        if type(self.neighbours['bottom']) is LightVoxel:
            self.visible_faces['bottom'] = False
        else:
            self.visible_faces['bottom'] = True
        # top
        if type(self.neighbours['top']) is LightVoxel:
            self.visible_faces['top'] = False
        else:
            self.visible_faces['top'] = True

    def calculate_unit_vertices(self):
        # calculate vertices of each voxel, i.e. 8 vertices of that unit cube, based on voxels coordinates
        # for every vertex create additional key global_vertex_number - will be needed when writing to 3mf
        # TODO: here a custom voxel scaling may be implemented e.g. non linear, parameterized and so
        # TODO: or not... if I keep implementing global point_space as well
        self.unit_vertices = [
            [
                [
                    [self._x, self._y, self._z, {'global_vertex_number': None}],
                    [self._x, self._y, self._z + 1, {'global_vertex_number': None}]
                ],
                [
                    [self._x, self._y + 1, self._z, {'global_vertex_number': None}],
                    [self._x, self._y + 1, self._z + 1, {'global_vertex_number': None}]
                ]
            ],
            [
                [
                    [self._x + 1, self._y, self._z, {'global_vertex_number': None}],
                    [self._x + 1, self._y, self._z + 1, {'global_vertex_number': None}]
                ],
                [
                    [self._x + 1, self._y + 1, self._z, {'global_vertex_number': None}],
                    [self._x + 1, self._y + 1, self._z + 1, {'global_vertex_number': None}]
                ]
            ]
        ]

        # TODO: TEMPORARY 1: here ad hock scaling
        # for i in range(2):
        #     for j in range(2):
        #         for k in range(2):
        #             v = self.unit_vertices[i][j][k]
        #             v[0] = v[0] * 5  # scale x
        #             v[1] = v[1] * 5  # scale y
        #             self.unit_vertices[i][j][k] = v

    def is_point_used(self, x, y, z) -> bool:
        # # is it my point? - is it on the unit_vertices list?

        # is it used by any of my visible faces
        for fn in self._face_names:
            if self.visible_faces[fn]:
                # get 2 triangles for every visible face
                triangle_1 = self._face_to_local_triangles[fn][0]
                triangle_2 = self._face_to_local_triangles[fn][1]
                point_used = False

                # if self._debug:
                #     print(self._x, self._y, self._z, 'point', [x, y, z], fn, 'Triangles: ', triangle_1, triangle_2)

                # check if [x,y,z] is used in a triangle
                def in_triangle(tr) -> bool:
                    for v in tr:
                        v_xp = self._vertex_to_coord[v][0]
                        v_yp = self._vertex_to_coord[v][1]
                        v_zp = self._vertex_to_coord[v][2]
                        v_point = self.unit_vertices[v_xp][v_yp][v_zp]
                        # if self._debug:
                        #     print('local triangle coords', v_xp, v_yp, v_zp)
                        #     print('global point', v_point)
                        if [v_point[0], v_point[1], v_point[2]] == [x, y, z]:
                            return True

                if in_triangle(triangle_1) or in_triangle(triangle_2):
                    point_used = True
                # if self._debug:
                #     print('point used:', point_used)

                if point_used:
                    return True

        return False

    def update_vertex_global_number(self, x, y, z, global_number):
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    v_point = self.unit_vertices[i][j][k]
                    if [x, y, z] == [v_point[0], v_point[1], v_point[2]]:
                        # global point located among own vertices, update global number
                        self.unit_vertices[i][j][k][3]['global_vertex_number'] = global_number
                        if self._debug:
                            print('global vertex number for', [x, y, z], 'updated to : ', global_number)

    def generate_triangles(self):
        # generate triangles based on visible faces, with reference to LightVoxelBox.global_vertices
        if self._debug:
            print('Generating triangles for ', self._x, self._y, self._z)
        triangles_global=[]
        for fn in self._face_names:
            if self.visible_faces[fn]:
                # get 2 triangles for every visible face
                triangle_1 = self._face_to_local_triangles[fn][0]
                triangle_2 = self._face_to_local_triangles[fn][1]

                # if self._debug:
                #     print(self._x, self._y, self._z, 'point', [x, y, z], fn, 'Triangles: ', triangle_1, triangle_2)

                triangle_1_global = []
                for v in triangle_1:
                    v_xp = self._vertex_to_coord[v][0]
                    v_yp = self._vertex_to_coord[v][1]
                    v_zp = self._vertex_to_coord[v][2]
                    this_vertex_global_number = self.unit_vertices[v_xp][v_yp][v_zp][3]['global_vertex_number']
                    triangle_1_global.append(this_vertex_global_number)
                if self._debug:
                    print(triangle_1_global)

                triangle_2_global = []
                for v in triangle_2:
                    v_xp = self._vertex_to_coord[v][0]
                    v_yp = self._vertex_to_coord[v][1]
                    v_zp = self._vertex_to_coord[v][2]
                    this_vertex_global_number = self.unit_vertices[v_xp][v_yp][v_zp][3]['global_vertex_number']
                    triangle_2_global.append(this_vertex_global_number)
                if self._debug:
                    print(triangle_2_global)

                # save globally expressed triangles to global triangle list of LightVoxelBox
                self._parent_box.global_triangles.append(triangle_1_global)
                self._parent_box.global_triangles.append(triangle_2_global)


# extended definition of LightVoxelBox class
class LightVoxelBox:
    """ This class is designed to convert an Image into lists of vertices and triangles """
    """ in a form that almost directly corresponds to 3mf format. """
    """ The conversion is based on certain simplifications and assumptions. """


    def _init_height_array(self):
        """ THIS IS NOT USED ANYMORE, but left for reference """
        # Translate an Image object into its representation as a 2D array of scalars
        # _height_array[x][y] contains information about the shade of the pixel at image[x][y]

        # TODO: create actual function - for now its only sample static data

        # # # very simple test height_map, manually created
        # self._height_array = [[2, 2, 2], [2, 3, 2], [2, 4, 2]]
        # self.x_max = 3  # size of image in pixel in the x axis
        # self.y_max = 3  # size of image in pixel in the y axis
        # self.z_max = 4  # maximum height, 'shade' found amongst image pixels


        self.process_image()

    def init_voxel_space(self):
        # Initiate a 3D array containing only None values. It will later hold references to particular voxels.

        # This array is created so that the addressing is _voxel_space[x][y][z]
        self.voxel_space = \
            [[[None for x in range(self.z_max)] for y in range(self.y_max)] for z in range(self.x_max)]
        pass

    def __init__(self, input_image: Image):
        # input Image
        self.image = input_image
        # a 3D array of LightVoxel objects
        self.voxel_space = None
        # a 3D array of points representing target 3D space
        self.point_space = None
        # a list of vertices in the point_space, each assigned a unique global_vertex_number
        self.global_vertices = None
        # a list of triangles referencing global_vertices
        self.global_triangles = None
        # a variable for holding the global vertex number generator object
        self.global_vertex_number = None
        self._point_space_z_max = None
        self._point_space_y_max = None
        self._point_space_x_max = None
        self.x_max = None
        self.y_max = None
        self.z_max = None
        self._height_array = None
        # self._init_height_array()
        # self._init_voxel_space()
        self._debug = False

    def process_image(self):
        if not issubclass(type(self.image), Image.Image):
            raise TypeError('Input image is not subclass of Image')

        self._height_array = []
        image_size = self.image.size
        if self._debug:
            print('Loaded image size: ', image_size)
        self.x_max = image_size[0]
        self.y_max = image_size[1]


        # initialize pixel-level access object
        pixels = self.image.load()

        # for x in range(self.x_max):
        #     for y in range(self.y_max):
        #         print(x, y, pixels[x, y])

        shade_min, shade_max = 0, 255

        for x in range(self.x_max):
            self._height_array.append([])
            for y in range(self.y_max):
                pixel_shade = pixels[x, y][0]
                pixel_height = int((255-pixel_shade)/25.5)
                if pixel_height > 10:
                    pixel_height = 10
                if pixel_height == 0:
                    pixel_height = 1
                self._height_array[x].append(pixel_height)

        self.z_max = 10



    def create_volume_voxels(self):
        # Initiate only these voxels (i.e. tuples of [x,y,z]) that are a park of target model
        # i.e. inside the model's volume

        # Create all voxels, so that for a given voxel (x,y,z) satisfies z<=h
        # where h = _height_array[x][y]. Put them in the _voxel_space structure
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    if self._height_array[x][y] > z:
                        v = LightVoxel(x, y, z, self)
                        self.voxel_space[x][y][z] = v
                        if self._debug:
                            print(v._x, v._y, v._z, 'in volume')

    def mark_invisible_voxels(self):
        # Ask every created voxel to evaluate if it's a boundry voxel, outer-most, visible one
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    v = self.voxel_space[x][y][z]
                    try:
                        v.check_invisible()
                    except AttributeError:
                        # 'empty' voxel - voxel_space[x][y][z]==None
                        pass
                    else:
                        if self._debug:
                            print(v._x, v._y, v._z, 'invisible: ', v.invisible)

    def connect_visible_face_sharing_vortices(self):
        # ask every voxel to find its neighbours
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    v = self.voxel_space[x][y][z]
                    try:
                        if not v.invisible:
                            v.find_neighbours()
                    except AttributeError:
                        # 'empty' voxel - voxel_space[x][y][z]==None
                        pass
                    else:
                        if self._debug:
                            print(v._x, v._y, v._z, 'neighbours: ', str(v.neighbours))

    def find_visible_voxels_visible_faces(self):
        # must be called after find_visible_voxels_visible_neighbours
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    v = self.voxel_space[x][y][z]
                    try:
                        if not v.invisible:
                            v.calculate_visible_faces()
                    except AttributeError:
                        # 'empty' voxel - voxel_space[x][y][z]==None
                        pass
                    else:
                        if self._debug:
                            print(v._x, v._y, v._z, v.visible_faces)

    def calculate_visible_voxels_unit_vertices(self):
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    v = self.voxel_space[x][y][z]
                    try:
                        if not v.invisible:
                            v.calculate_unit_vertices()
                    except AttributeError:
                        # 'empty' voxel - voxel_space[x][y][z]==None
                        pass
                    else:
                        if self._debug:
                            print(v._x, v._y, v._z, v.unit_vertices)

    def init_point_space(self):
        # initiate a 3D point space of potential vertices
        # this will hold global vertex numbers
        # TODO: this must be coherent with potential mapping from inside LightVoxel
        # TODO: for now static, that assumes every voxel is 1x1x1 in size
        self.point_space = \
            [[[None for x in range(self.z_max*2)] for y in range(self.y_max*2)] for z in range(self.x_max*2)]
        self._point_space_z_max = self.z_max * 2

        self._point_space_y_max = self.y_max * 2
        self._point_space_x_max = self.x_max * 2

    def global_vertex_number_gen(self):
        n = 0
        while True:
            yield n
            n += 1

    def generate_visible_faces_global_vertices_numbers(self):
        # go through all relevant voxels and assign a global number to every vertex of each voxel
        # while also keeping track of redundant vertices - they must get the same global number
        # let the voxels know what global numbers their vertices got

        self.global_vertex_number = self.global_vertex_number_gen()
        self.global_vertices = []

        # just an internal convinience wrapper function
        def create_global_vertex_update_voxel(x: int, y: int, z: int, v: LightVoxel):
            # create new global vertex by assigning it a number and appending to global_vertices_list
            # let the current voxel know what global number it's particular vertex has

            # new_number = None
            if self.point_space[x][y][z] is None:
                # # this point is new, generate global number and add to the list
                # assign new global vertex number
                new_number = next(self.global_vertex_number)
                self.point_space[x][y][z] = new_number
                # update the global_vertices list
                self.global_vertices.append(((x, y, z), new_number))
            else:
                # # this point already assigned a global number, just get it
                new_number = self.point_space[x][y][z]

            # tell the voxel to save globalvertex number for its point
            v.update_vertex_global_number(x, y, z, new_number)

            if self._debug:
                print('point', [x, y, z], 'assigned global number', self.point_space[x][y][z])

        # go through all points for all voxels
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    # getting each voxel v in the whole voxel space
                    v = self.voxel_space[x][y][z]
                    # if voxel exists at given coordinates and is visible at all
                    if type(v) is LightVoxel and not v.invisible:
                        for px in range(self._point_space_x_max):
                            for py in range(self._point_space_y_max):
                                for pz in range(self._point_space_z_max):
                                    # getting each point v in the point_space
                                    if v.is_point_used(px,py,pz):
                                        if self._debug:
                                            print(v._x, v._y, v._z, 'uses point', [px, py, pz])
                                        create_global_vertex_update_voxel(px, py, pz, v)

    def generate_global_triangles(self):
        # go through all relevant voxels and ask them
        # to calculate their visible triangles in terms of global_vertices
        self.global_triangles = []
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    # getting each voxel v in the whole voxel space
                    v = self.voxel_space[x][y][z]
                    # if voxel exists at given coordinates and is visible at all
                    if type(v) is LightVoxel and not v.invisible:
                        v.generate_triangles()

    def __str__(self):
        s = ''
        s += 'LightVoxelBox object\n'
        s += f' Source image dimensions (x, y):    ({self.x_max}, {self.y_max})\n'
        s += f' Voxel space dimensions (x, y, z):  ({self.x_max}, {self.y_max}, {self.z_max})\n'
        s += f' Vertex space dimensions (x, y, z): ' \
            f'({self._point_space_x_max}, {self._point_space_y_max}, {self._point_space_z_max})\n'
        s += f' # global vertices generated:       {len(self.global_vertices)}\n'
        s += f' # global triangles generated:      {len(self.global_triangles)}\n'

        return s


# definition of LightVoxelBox_writer class
class LightVoxelBoxWriter:
    """ this class is designed to format global vertices and triangels list from LightVoxelBox object """
    """ and put them into the actual 3mf file and package """

    def __init__(self, voxel_box: LightVoxelBox):
        self.voxel_box = voxel_box
        self.xml_root = None  # :ET.Element
        self.xml_vertices = None  # :ET.Element
        self.xml_triangles = None  # :ET.Element
        self._debug = True

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


""" Open an image """
image = Image.open('sample_image.bmp')

""" Generate 3mf-compatibile lists of vertices and traingles that represent the input image """
# create LightVoxelBox main object
b = LightVoxelBox(image)

# create height_array
print('b.process_image()')
b.process_image()

# initialize voxel space
print('b.init_voxel_space()')
b.init_voxel_space()

# create voxels that represent the volume of the model based on input Image
print('b.create_volume_voxels()')
b.create_volume_voxels()

# check which voxels will not be visible and mark them as such
print('b.mark_invisible_voxels()')
b.mark_invisible_voxels()

# ask all visible voxels to find their immediate neighbours
# (does this feel like a 'lower level' function then surroundings somehow??)
print('b.connect_visible_face_sharing_vortices()')
b.connect_visible_face_sharing_vortices()

# ask all visible voxels to calculte their visible faces
# based on immediate neighbours or their lack of
print('b.find_visible_voxels_visible_faces()')
b.find_visible_voxels_visible_faces()

# ask all visible voxels to calculate their unit vertices, that is coordinates in 3D space
# assuming their all cubes of size (1,1,1)
print('b.calculate_visible_voxels_unit_vertices()')
b.calculate_visible_voxels_unit_vertices()

# construct an array that represents physical coordinates and their global_vertex_numbers
print('b.init_point_space()')
b.init_point_space()

# generate global numbers for required vertices, place them in point_space array
# and also let voxels know what global numbers their local vertices have
# construct a list of global points
print('b.generate_visible_faces_global_vertices_numbers()')
b.generate_visible_faces_global_vertices_numbers()

# generate list of global triangles
print('b.generate_global_triangles()')
b.generate_global_triangles()

print(str(b))


""" Save vertices and triangles lists from LightVoxelBox into 3mf package"""
s = LightVoxelBoxWriter(b)
s.create_3mf_structure()
s.fill_xml_vertices()
s.fill_xml_triangles()
s.save_3mf()