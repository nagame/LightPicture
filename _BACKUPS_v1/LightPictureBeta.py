from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil


class LightVoxelBox():
    pass


class LightVoxel:
    pass


class LightVoxel():
    def __init__(self, x, y, z, parent: LightVoxelBox):
        [self._x, self._y, self._z] = [x, y, z]
        self._parent_box = parent

    def check_boundry(self):
        # Evaluate if self is a boundary voxel

        # check if there is at least one side not covered by other voxel

        pass


class LightVoxelBox():
    def _init_height_array(self):
        # Translate an Image object into its representation as a 2D array of scalars
        # _height_array[x][y] contains information about the shade of the pixel at image[x][y]

        # TODO: create actual function - for now its only sample static data

        self._height_array = [[1, 2], [3, 4]]
        self._x_max = 2  # size of image in pixel in the x axis
        self._y_max = 2  # size of image in pixel in the y axis
        self._z_max = 4  # maximum height, 'shade' found amongst image pixels

    def _init_voxel_space(self):
        # Initiate a 3D array containing only None values. It will later hold references to particular voxels.

        # This array is created so that the addressing is _voxel_space[x][y][z]
        self._voxel_space = \
            [[[None for x in range(self._z_max)] for y in range(self._y_max)] for z in range(self._x_max)]
        pass

    def __init__(self):
        self._init_height_array()
        self._init_voxel_space()

    def create_bounding_voxels(self):
        # Initiate only these voxels (i.e. tuples of [x,y,z]) that are the outer-most and visible

        # Create all voxels, so that for a given voxel (x,y,z) satisfies z<=h
        # where h = _height_array[x][y]. Put them in the _voxel_space structure
        for x in range(self._x_max):
            for y in range(self._y_max):
                for z in range(self._z_max):
                    if self._height_array[x][y] > z:
                        v = LightVoxel(x, y, z, self)
                        self._voxel_space[x][y][z] = v

        # Ask every created voxel to evaluate if it's a boundry voxel, outer-most, visible one
        for x in range(self._x_max):
            for y in range(self._y_max):
                for z in range(self._z_max):
                    v = self._voxel_space[x][y][z]


b = LightVoxelBox()
b.create_bounding_voxels()
