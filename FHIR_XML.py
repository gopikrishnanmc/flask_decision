import xml.etree.ElementTree as ET


tree = ET.parse('XML/sample.xml')

def iter_x():
    root = tree.getroot()
    for elem in root.getiterator():
        print (elem.tag, elem.attrib)

iter_x()