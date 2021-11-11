from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil


# initial definition of LightVoxelBox for references
class LightVoxelBox:
    def __init__(self):
        self.voxel_space = None
        self._debug = True


# initial definition of LightVoxel for references
class LightVoxel:
    def __init__(self):
        self._debug = True


# extended definition of LightVoxel
class LightVoxel:
    def __init__(self, x, y, z, parent: LightVoxelBox):
        [self._x, self._y, self._z] = [x, y, z]
        self._parent_box = parent
        self._debug = True
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
                    ['x0', 'y0', 'z0'],
                    ['x0', 'y0', 'z1']
                ],
                [
                    ['x0', 'y1', 'z0'],
                    ['x0', 'y1', 'z1']
                ]
            ],
            [
                [
                    ['x1', 'y0', 'z0'],
                    ['x1', 'y0', 'z1']
                ],
                [
                    ['x1', 'y1', 'z0'],
                    ['x1', 'y1', 'z1']
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
        # Evaluate if self is invisible
        # that is: check if all sides covered by other voxels

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

    def is_point_used(self, x, y, z) -> bool:
        # # is it my point? - is it on the unit_vertices list?
        # point_in_unit_vertices = False
        # for i in range(2):
        #     for j in range(2):
        #         for k in range(2):
        #             if [x, y, z] == self.unit_vertices[x][y][z]:
        #                 point_in_unit_vertices = True
        #
        # if not point_in_unit_vertices:
        #     return False

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


    # def generate_global_vertices_numbers(self):
    #     # use the generator from LightVoxelBox to number own vertices
    #     # check all neighbours first, to see if any common vertices have already been assigned a global number
    #     # if not, then assign it
    #
    #     def assign_gvn(v):
    #         # check all vertices of all neighbours to find duplicates
    #         pass
    #
    #     # call assign_gvn for every own vertex
    #     assign_gvn(self.unit_vertices[0][0][0])
    #     # assign_gvn(self.unit_vertices[0][0][0])
    #     # assign_gvn(self.unit_vertices[0][0][0])
    #     # assign_gvn(self.unit_vertices[0][0][0])
    #     # assign_gvn(self.unit_vertices[0][0][0])
    #     # assign_gvn(self.unit_vertices[0][0][0])
    #     # assign_gvn(self.unit_vertices[0][0][0])
    #     # assign_gvn(self.unit_vertices[0][0][0])
    #
    #
    #     # print(next(self._parent_box.global_vertex_number))


class LightVoxelBox():
    def _init_height_array(self):
        # Translate an Image object into its representation as a 2D array of scalars
        # _height_array[x][y] contains information about the shade of the pixel at image[x][y]

        # TODO: create actual function - for now its only sample static data

        self._height_array = [[2, 2, 2], [2, 3, 2], [2, 4, 2]]
        self.x_max = 3  # size of image in pixel in the x axis
        self.y_max = 3  # size of image in pixel in the y axis
        self.z_max = 4  # maximum height, 'shade' found amongst image pixels

    def _init_voxel_space(self):
        # Initiate a 3D array containing only None values. It will later hold references to particular voxels.

        # This array is created so that the addressing is _voxel_space[x][y][z]
        self.voxel_space = \
            [[[None for x in range(self.z_max)] for y in range(self.y_max)] for z in range(self.x_max)]
        pass

    def __init__(self):
        self.voxel_space = None
        self.point_space = None
        self._point_space_z_max = None
        self._point_space_y_max = None
        self._point_space_x_max = None
        self.global_vertex_number = None
        self._height_array = None
        self._debug = True
        self._init_height_array()
        self._init_voxel_space()

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

    def generate_visible_voxels_global_vertices_numbers(self):
        # will need to go through all relevant voxels and assign a global number to every vertex of each voxel
        # while also keeping track of redundant vertices - they must get the same global number
        self.global_vertex_number = self.global_vertex_number_gen()
        # for x in range(self.x_max):
        #     for y in range(self.y_max):
        #         for z in range(self.z_max):
        #             v = self.voxel_space[x][y][z]
        #             if type(v) is LightVoxel:
        #                 for px in range(self._point_space_x_max):
        #                     for py in range(self._point_space_y_max):
        #                         for pz in range(self._point_space_z_max):
        #                             if v.is_point_used(px,py,pz):
        #                                 print(v._x, v._y, v._z, 'uses point', [x, y, z])

        for x in range(1):
            for y in range(1):
                for z in range(1):
                    v = self.voxel_space[x][y][z]
                    if type(v) is LightVoxel:
                        for px in range(self._point_space_x_max):
                            for py in range(self._point_space_y_max):
                                for pz in range(self._point_space_z_max):
                                    if v.is_point_used(px,py,pz):
                                        print(v._x, v._y, v._z, 'uses point', [x, y, z])


    # is this necessary? not used for now
    def delete_invisible_voxels(self):
        # must only be called after mark_invisible_voxels
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    v = self.voxel_space[x][y][z]
                    try:
                        if v.invisible:
                            # 'delete' the voxel if marked as invisible
                            self.voxel_space[x][y][z] = None
                    except AttributeError:
                        # 'empty' voxel - voxel_space[x][y][z]==None
                        pass




# create LightVoxelBox main object
b = LightVoxelBox()
# create voxels that represent the volume of the model based on input Image
b.create_volume_voxels()
# check which voxels will not be visible and mark them as such
b.mark_invisible_voxels()
# ask all visible voxels to find their immediate neighbours
# (does this feel like a 'lower level' function then surroundings somehow??)
b.connect_visible_face_sharing_vortices()
# ask all visible voxels to calculte their visible faces
# based on immediate neighbours or their lack of
b.find_visible_voxels_visible_faces()
# ask all visible voxels to calculate their unit vertices, that is coordinates in 3D space
# assuming their all cubes of size (1,1,1)
b.calculate_visible_voxels_unit_vertices()
b.init_point_space()
b.generate_visible_voxels_global_vertices_numbers()



