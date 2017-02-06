import subprocess
import sys
import networkx as nx
import os
import xml.etree.ElementTree as ET
from gen_config import ConfigGen

G = nx.DiGraph()
nw_dict = {}
intervals = [(0,1000),(1000,2000),(2000,3000)]

def start():
	create_networkx()
	rerouters,vul_edges = place_rerouters()
	destinations = get_destinations()
	#print(rerouters)
	cg = ConfigGen(network=nw_dict, intervals=intervals, rerouters=rerouters, vul_edges=vul_edges, sources=vul_edges, destinations=destinations)
	cg.generate()
	cg.generate_trips(total_cars=1000)

def create_networkx():
	#Import network file
	tree = ET.parse('../network/sf_net.net.xml') 
	root = tree.getroot()
	for child in root:
		if child.tag == 'edge' and 'function' not in child.attrib:
			#print(child.attrib)
			nw_dict[int(child.attrib['id'])] = (int(child.attrib['from']),int(child.attrib['to']))
	for key in sorted(nw_dict.keys()):
		#print(key, nw_dict[key])
		G.add_edge(nw_dict[key][0],nw_dict[key][1])

def place_rerouters():
	vul_edges = parse_edges('../network/all_edges.txt')
	rerouters = {}
	for edge in vul_edges:
		edges = G.in_edges([nw_dict[edge][0], nw_dict[edge][1]])
		edge_names = []
		for e in edges:
			for key in nw_dict.keys():
				#print(e, nw_dict[key])
				if e == nw_dict[key]:
					edge_names.append(key)
		rerouters[edge] = edge_names
	return rerouters,vul_edges

def get_destinations():
	return parse_edges('../network/exit_edges.txt')


def parse_edges(filename):
	edges = []
	with open(filename) as fn:
		for line in fn.readlines():
			if 'edge' in line:
				edges.append(int(line[5:]))
	return edges




if __name__=='__main__':
    start()
    print("Done")
