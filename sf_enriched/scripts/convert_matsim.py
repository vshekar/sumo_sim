"""
This script converts the matsim population demand file to SUMO by converting the 
starting point in MATsim to its nearest edge in SUMO.

"""
import xml.etree.ElementTree as ET
import sumolib
from operator import itemgetter



def parse_matsim_demand():
	demand = []
	net = sumolib.net.readNet('SF_sumo.net.xml')
	tree = ET.parse('Siouxfalls_population_matsim.xml')
	root = tree.getroot()
	total_count = 0
	car_not_avail = 0
	x_offset = -679322.03
	y_offset = -4820339.81
	for person in root:
		if person.tag == 'person':
			for plan in person:
				p = []
				for act in plan:
					if act.tag == 'act':
						if 'end_time' in act.attrib:
							t = convert_time(act.attrib['end_time'])
						else:
							t = 0
						x = float(act.attrib['x']) + x_offset
						y = float(act.attrib['y']) + y_offset
						start = get_nearest_edge(net, x, y)
						p.append((t,start))
				for i in range(len(p)-1):
					start_time = p[i][0]
					start_edge = p[i][1]
					end_edge = p[i+1][1]
					demand.append((start_time,start_edge,end_edge))
	generate_trip_file(demand)
	print(len(demand))

def generate_trip_file(demand):
	demand = sorted(demand,key=itemgetter(0))
	string = '<?xml version="1.0"?>\n<trips>\n'
	count = 0
	for trip in demand:
		string += '<trip id="{}" depart="{}" departLane="best" departPos="random_free" departSpeed="max" arrivalPos="0" from="{}" to="{}"/>\n'.format(count, trip[0], trip[1], trip[2])
		count += 1
	string += '</trips>'
	with open('trip.xml','w') as f:
		f.write(string)



def get_nearest_edge(net, x, y):
	edges = []
	radius = 20
	while len(edges) ==0:
		edges = net.getNeighboringEdges(x, y, radius)
		radius += 10
	return edges[0][0].getID()


def convert_time(time):
	#Converts 24 hour time to simulation seconds starting from 06:00:00
	hr,mn,sc = time.split(":")
	hr,mn,sc = int(hr),int(mn),int(sc)
	sim_time = sc + 60*(mn)
	if hr-6 < 0:
		sim_time += (24+(hr-6))*3600
	else:
		sim_time += (hr-6)*3600

	return sim_time


if __name__=="__main__":
	parse_matsim_demand()