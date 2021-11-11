from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import shutil


# ---------------========  I M A G E  ======-----------------
im = Image.open('sample_image.bmp')

# get image size
print(im.size)

# load direct pixel access object
px = im.load()

# get rgb value at pixel
print(px[0, 0])
print(px[2, 1])
print(px[1, 2])


# # # ---------------========  3MF  XML  ======-----------------
def save_3mf(xml_root: ET.Element):
    # # # Save 3mf xml structure to a file and make it a legit 3mf package
    # create folder named "3D"
    try:
        os.mkdir('ZIP')
        os.mkdir('ZIP/3D')
    except FileExistsError:
        pass
    # make xml pretty and save xml file as "[name].model"
    xmlstr = minidom.parseString(ET.tostring(xml_root)).toprettyxml(indent="   ")
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


def create_3mf_structure() -> ET.Element:
    # main xml element - "model". XML Root element.
    mf_model = ET.Element('model')
    mf_model.attrib['unit'] = 'millimeter'

    # # 3mf "resources" element:
    # xml element - "model" -> "resources"
    mf_resources = ET.SubElement(mf_model, 'resources')
    # xml element - "model" -> "resources" -> "object"
    mf_object = ET.SubElement(mf_resources, 'object')
    mf_object.attrib['type'] = 'model'
    mf_object.attrib['id'] = '1'
    # xml element - "model" -> "resources" -> "object" -> "mesh"
    # this will contain ACTUAL 3d object data: vertices and triangles
    mf_mesh = ET.SubElement(mf_object, 'mesh')
    # xml element - "model" -> "resources" -> "object" -> "mesh" -> "vertices"
    mf_vertices = ET.SubElement(mf_mesh, 'vertices')
    # xml element - "model" -> "resources" -> "object" -> "mesh" -> "triangles"
    mf_triangles = ET.SubElement(mf_mesh, 'triangles')
    # xml element - "model" -> "resources" -> "object" -> "mesh" -> "components"
    mf_components = ET.SubElement(mf_mesh, 'components')

    # # 3mf "build" element:
    # xml element - "model" -> "build": this will reference just a single 3D based on "resources"
    mf_build = ET.SubElement(mf_model, 'build')
    # xml element - "model" -> "build" -> "item"
    mf_item = ET.SubElement(mf_build, 'item')
    mf_item.attrib['objectid'] = '1'

    return mf_model


def automesh(vertices: ET.Element, triangles: ET.Element):
    # # add vertex example:
    # vert = ET.SubElement(mf_vertices, 'vertex')
    # vert.attrib['x'] = '0'
    # vert.attrib['y'] = '100'
    # vert.attrib['z'] = '0'
    # # add triangle example:
    # tria = ET.SubElement(mf_triangles, 'triangle')
    # tria.attrib['v1'] = '0'
    # tria.attrib['v2'] = '2'
    # tria.attrib['v3'] = '1'

    pass










mf_model = create_3mf_structure()
mf_vertices = mf_model.find('resources').find('object').find('mesh').find('vertices')
mf_triangles = mf_model.find('resources').find('object').find('mesh').find('triangles')

# # # Create en example mesh - simple triangular pyramid lets say
# # Add 4 vertices, each has 3 space coordinates: x,y,z
vert = ET.SubElement(mf_vertices, 'vertex')
vert.attrib['x'] = '0'
vert.attrib['y'] = '0'
vert.attrib['z'] = '0'
vert = ET.SubElement(mf_vertices, 'vertex')
vert.attrib['x'] = '100'
vert.attrib['y'] = '0'
vert.attrib['z'] = '0'
vert = ET.SubElement(mf_vertices, 'vertex')
vert.attrib['x'] = '0'
vert.attrib['y'] = '100'
vert.attrib['z'] = '0'
vert = ET.SubElement(mf_vertices, 'vertex')
vert.attrib['x'] = '25'
vert.attrib['y'] = '25'
vert.attrib['z'] = '50'
# # Add 4 triangles - vertices order is crucial
tria = ET.SubElement(mf_triangles, 'triangle')
tria.attrib['v1'] = '1'
tria.attrib['v2'] = '2'
tria.attrib['v3'] = '3'
tria = ET.SubElement(mf_triangles, 'triangle')
tria.attrib['v1'] = '0'
tria.attrib['v2'] = '3'
tria.attrib['v3'] = '2'
tria = ET.SubElement(mf_triangles, 'triangle')
tria.attrib['v1'] = '0'
tria.attrib['v2'] = '2'
tria.attrib['v3'] = '1'
tria = ET.SubElement(mf_triangles, 'triangle')
tria.attrib['v1'] = '0'
tria.attrib['v2'] = '1'
tria.attrib['v3'] = '3'



save_3mf(mf_model)

