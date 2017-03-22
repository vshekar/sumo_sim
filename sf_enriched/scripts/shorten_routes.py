import xml.etree.ElementTree as ET




tree = ET.parse('route.rou.xml')
root = tree.getroot()

for vehicle in root:
	for route in vehicle:
		rt = route.attrib['edges'].split()
		l = int(len(rt)/2)
		if l >1:
			route.attrib['edges'] = ' '.join(rt[0:l])


tree.write('new_route.rou.xml')
		
