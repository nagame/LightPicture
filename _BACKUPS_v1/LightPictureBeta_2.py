from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil


# # initial definition of LightVoxelBox for references
# class LightVoxelBox:
#     def __init__(self):
#         self.voxel_space = None
#         self._debug = True
#
#
# # initial definition of LightVoxel for references
# class LightVoxel:
#     def __init__(self):
#         self._debug = True


# extended definition of LightVoxel
class LightVoxel:
    def __init__(self, x, y, z, parent: LightVoxelBox):
        [self._x, self._y, self._z] = [x, y, z]
        self._parent_box = parent
        self._debug = True
        self.invisible = None
        self.visible_faces = {
            "front": None,
            "back": None,
            "left": None,
            "right": None,
            "top": None,
            "bottom": None,
        }

    def check_invisible(self):
        # Evaluate if self is a boundary voxel

        # # check if all sides covered by other voxels
        # set invisible to True, will check  all cases that could change this
        self.invisible = True
        # check if self has any coordinate equal to 0
        # this has to be checked because array[-1] does not yield exception
        if self._x == 0 or self._y == 0 or self._z == 0:
            self.invisible = False
            return

        # no check if any neighbouring voxel is None or outside the voxel_space
        try:
            # get all relevant neighbouring voxels
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
        else:
            # if any of them is None ('empty') then self is not invisible
            for n in neighbours:
                if n is None:
                    self.invisible = False

    def calculate_visible_faces(self):
        # calculate and save which faces of self are gonna be visible

        # this function is designed to be called only after invoking
        # create_volume_voxels() and then mark_invisible_voxels()
        # from LightVoxelBox object

        # no visible faces if voxel marked invisible as a whole
        if self.invisible:
            return

        # # now, all faces will be visible on self, except these that have invisible neighbour
        # try gettin all neighbours, ignore voxel_space IndexError
        neighbours = []
        try:
            neighbours = [
                self._parent_box.voxel_space[self._x - 1][self._y][self._z],  # left
                self._parent_box.voxel_space[self._x + 1][self._y][self._z],  # right
                self._parent_box.voxel_space[self._x][self._y - 1][self._z],  # front
                self._parent_box.voxel_space[self._x][self._y + 1][self._z],  # back
                self._parent_box.voxel_space[self._x][self._y][self._z - 1],  # bottom
                self._parent_box.voxel_space[self._x][self._y][self._z + 1]   # top
            ]
        except IndexError:
            pass

        for n in neighbours:
            # left
            if neighbours[0] is LightVoxel and neighbours[0].invisible:
                self.visible_faces['left'] = False
            else:
                self.visible_faces['left'] = True
            # right
            if neighbours[1] is LightVoxel and neighbours[1].invisible:
                self.visible_faces['right'] = False
            else:
                self.visible_faces['right'] = True
            # front
            if neighbours[2] is LightVoxel and neighbours[2].invisible:
                self.visible_faces['front'] = False
            else:
                self.visible_faces['front'] = True
            # back
            if neighbours[3] is LightVoxel and neighbours[3].invisible:
                self.visible_faces['back'] = False
            else:
                self.visible_faces['back'] = True
            # bottom
            if neighbours[4] is LightVoxel and neighbours[4].invisible:
                self.visible_faces['bottom'] = False
            else:
                self.visible_faces['bottom'] = True
            # top
            if neighbours[5] is LightVoxel and neighbours[5].invisible:
                self.visible_faces['top'] = False
            else:
                self.visible_faces['top'] = True


# extended definition of LightVoxelBox
class LightVoxelBox():
    def _init_height_array(self):
        # Translate an Image object into its representation as a 2D array of scalars
        # _height_array[x][y] contains information about the shade of the pixel at image[x][y]

        # TODO: create actual function - for now its only sample static data

        self._height_array = [[2, 2, 2], [2, 3, 2], [2, 2, 2]]
        self.x_max = 3  # size of image in pixel in the x axis
        self.y_max = 3  # size of image in pixel in the y axis
        self.z_max = 3  # maximum height, 'shade' found amongst image pixels

    def _init_voxel_space(self):
        # Initiate a 3D array containing only None values. It will later hold references to particular voxels.

        # This array is created so that the addressing is _voxel_space[x][y][z]
        self.voxel_space = \
            [[[None for x in range(self.z_max)] for y in range(self.y_max)] for z in range(self.x_max)]
        pass

    def __init__(self):
        self.voxel_space = None
        self._height_array = None
        self._debug = True
        self._init_height_array()
        self._init_voxel_space()

    def create_volume_voxels(self):
        # Initiate only these voxels (i.e. tuples of [x,y,z]) that are a park of target model

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

    def calculate_voxels_visible_faces(self):
        # must be called before delete_invisible_voxels
        for x in range(self.x_max):
            for y in range(self.y_max):
                for z in range(self.z_max):
                    v = self.voxel_space[x][y][z]
                    try:
                        v.calculate_visible_faces()
                    except AttributeError:
                        # 'empty' voxel - voxel_space[x][y][z]==None
                        pass
                    else:
                        if self._debug:
                            print(v._x, v._y, v._z, v.visible_faces)

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




b = LightVoxelBox()
b.create_volume_voxels()
b.mark_invisible_voxels()
# b.calculate_voxels_visible_faces()
b.delete_invisible_voxels()
