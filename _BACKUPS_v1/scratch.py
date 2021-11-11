from PIL import Image
import xml.etree.ElementTree as ET
from xml.dom import minidom

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

# ---------------========  X   M   L  ======-----------------
# Create simple XML structure
root = ET.Element('root')
b = ET.SubElement(root, 'branch')
c = ET.SubElement(b, 'subbranch')
ET.dump(root)

# Write xml tree to file
tree = ET.ElementTree(root)
with open('sample_xml.xml', 'wb') as f:
    tree.write(f)



# # # ---------------========  3MF  XML  ======-----------------
# # # Create simple 3MF file XML structure

# main xml element - "model". XML Root element.
mf_model = ET.Element('model')

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

# # 3mf "build" element:
# xml element - "model" -> "build": this will reference just a single 3D based on "resources"
mf_build = ET.SubElement(mf_model, 'build')
# xml element - "model" -> "build" -> "item"
mf_item = ET.SubElement(mf_build, 'item')
mf_item.attrib['objectid'] = '1'

# make xml pretty and print to file
xmlstr = minidom.parseString(ET.tostring(mf_model)).toprettyxml(indent="   ")
with open("sample_xml.xml", "w") as f:
    f.write(xmlstr)
