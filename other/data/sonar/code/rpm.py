# remove paragrap level markables

import os
import xml.etree.ElementTree as ET


for filename in os.listdir("Markables"):
    
    
    if filename.endswith("np_level.xml"):
        f = filename[:-12]
        paragraph_file = "Markables/" + f + "paragraph_level.xml"
        paragraph_tree = ET.parse(paragraph_file)
        paragraph_root = paragraph_tree.getroot()
        
        np_tree = ET.parse("Markables/" + filename)
        np_root = np_tree.getroot()
        
        markables = [child.attrib["id"] for child in paragraph_root]
        
        for child in np_root:
            if child.attrib["id"] in markables:
                np_root.remove(child)
