import xml.etree.ElementTree as ET
import math



tree = ET.parse('../trips/route.rou.xml')
root = tree.getroot()

for vehicle in root:
	for route in vehicle:
		rt = route.attrib['edges'].split()
		l = int(len(rt)/2)
		if l >1:
			start = math.ceil(l/2)
			end = -1 * math.floor(l/2)
			route.attrib['edges'] = ' '.join(rt[start:end])


tree.write('../trips/new_route.rou.xml')
		
