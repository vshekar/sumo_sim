
#!/usr/bin/env python
#
from imposm.parser import OSMParser
from graph_tool.all import *
from sets import Set
from datetime import datetime
import graph_tool.util as gtu
import sys, argparse, logging, math
import xml.etree.cElementTree as ET

# Gather our code in a main() function
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
    #Initialize MapParser object
    map_parser = MapParser()
    map_parser.run(args)
  
class MapParser(object):
    #List of road types excluded from parsing
    highways_excluded = ['steps','footway','pedestrian']
    num_nodes = 0
    num_roads = 0

    def run(self,args):
        self.extract_network(args.osm_filename)
        if args.draw:
            self.draw(args.draw)
        if args.output:
            self.tntp(args.output)
        if args.vissim:
            self.vissim(args.vissim)

    def extract_network(self,osm_filename):
        self.ne = NetworkExtractor()
        self.ne.extract(osm_filename)
        
    def vissim(self, filename):
        """Data required for VISSIM file. 
        Links : Link num, # of lanes (and
        width), Series of x,y,z points in the direction of traffic flow,
        Connectors: Connector # starting from 10000, # of lanes w/o width,
        fromLinkEndPt lane="link# lane#" pos="dist of link#"
        toLinkEndPt lane="link# lane#" pos="dist origin of link (Usually 0)",
        Series of x,y,z points usually 2 points
        
        tree = ET.parse("reference_inpx.inpx")
        root = tree.getroot()
        for link in root.findall("./links/link"):
            print link.attrib['no']
            if int(link.attrib['no']) < 10000:
                print "Regular link"
                for point in link.findall("./geometry/points3D/point3D"):
                    print point.attrib['x'], point.attrib['y']
            else:
                print "Connectors!"
                for point in link.findall("./geometry/points3D/point3D"):
                    print point.attrib['x'], point.attrib['y']
                    
                    
        To add XML:
	  link = ET.SubElement(root[0],'link')
	  link.set('attrib','value')
	  lanes = ET.SubElement(link,'lanes')
	  lane = ET.SubElement(lanes,'lane')
	  lane.set('attrib','value')
	  tree = ET.cElementTree(root)
	  tree.write('test.inpx')
        """
        #First Parse the graph into links and connectors
        #vertices = (gtu.find_vertex_range(self.g,"in",[2,1000]))
        #ver2 =  gtu.find_vertex_range(self.g,"out",[2,1000])
        
        #vert_zero = gtu.find_vertex_range(self.g,"in",[0,0]) 
        #vert_zero2 = gtu.find_vertex_range(self.g,"out",[0,0])
        #print len(vertices) , len(ver2), len(vert_zero), len(vert_zero2)
        #for vertex in vertices+vert_zero:
        #    print str(self.vertex_properties['pos'][vertex][1])+','+str(self.vertex_properties['pos'][vertex][0])
        print len(self.ne.edge_endpts)
        print len(self.ne.link_list)
        
        tree = ET.parse("reference_inpx.inpx")
        root = tree.getroot()
        


    def draw(self,op_filename):
        graph_draw(self.ne.g,vertex_size=self.ne.vertex_properties['size'], 
                pos=self.ne.vertex_properties['pos'],
                edge_pen_width=self.ne.edge_properties['thickness'],
                edge_end_marker=self.ne.edge_properties['marker'],
                fit_view=True,output_size=(800,800),output=args.draw)

class NetworkExtractor(object):
    nodes = 0
    hw = 0
    counter = 0
    g = Graph()
    osm_to_graph = {}
    highway_nodes = Set()
    edge_endpts = []
    link_list = []
    
    #Network vertex visual properties
    vprop_pos = g.new_vertex_property("vector<double>")
    vprop_size = g.new_vertex_property("double")
    vprop_shape = g.new_vertex_property("double")
    vprop_text = g.new_vertex_property("string")
    vprop_font_size = g.new_vertex_property("int")
    vprop_text_rotation = g.new_vertex_property("double")
    vprop_fill_color = g.new_vertex_property("vector<double>")
    vertex_properties = {
                        'pos':vprop_pos,
                        'size':vprop_size,
                        'shape':vprop_shape,
                        'text':vprop_text,
                        'font_size':vprop_font_size,
                        'text_rotation':vprop_text_rotation,
                        'fill_color':vprop_fill_color,
                        }
    node_size = 2.0
    
    #Network edge visual properties
    eprop_marker = g.new_edge_property("double")
    eprop_thickness = g.new_edge_property("double")
    edge_properties = {
                        'marker':eprop_marker,
                        'thickness':eprop_thickness
                        }

    
    #List of road types excluded from parsing
    highways_excluded = ['steps','footway', 'pedestrian']

    def extract(self,osm_filename):
        self.p = OSMParser(ways_callback=self.find_highway_nodes)
        self.p.parse(osm_filename)
        print "Highway nodes found"
        self.p =  OSMParser(coords_callback=self.count_nodes)
        self.p.parse(osm_filename)
        print "Created graph nodes"
        self.p = OSMParser(ways_callback=self.connect_nodes)
        self.p.parse(osm_filename)
        print len(self.edge_endpts)
        #return self.g,self.vertex_properties,self.edge_properties,self.edge_endpts

    def find_highway_nodes(self, ways):
       """Find all nodes with the tag 'Highway'"""
       for osm_id, tags, refs in ways:
            if 'highway' in tags and tags['highway'] not in self.highways_excluded:
                for r in refs:
                    self.highway_nodes.add(r)

    def count_nodes(self,nodes):
        """Counts the total number of nodes in a particular way"""
        for osm_id, lat, lng in nodes:
            if osm_id in self.highway_nodes:
                #Note: OSM ids are unique. Node numbers in the graph start from
                #0. The osm_to_graph dict associates osm id to node number.
                self.osm_to_graph[osm_id] = self.nodes
                self.g.add_vertex()
                self.vprop_pos[self.g.vertex(self.nodes)] = [lng,lat]
                self.nodes += 1

    def connect_nodes(self, ways):
        """Adds edges to the graph"""
        for osm_id,tags,refs in ways:
            if ('highway' in tags and tags['highway'] not in
                self.highways_excluded):
                link = []
                self.hw += 1
                for i in range(len(refs) -1):
                    if (refs[i] in self.osm_to_graph and refs[i+1] in
                        self.osm_to_graph):
                        v1 = self.g.vertex(self.osm_to_graph[refs[i]])
                        v2 = self.g.vertex(self.osm_to_graph[refs[i+1]])
                        
                        if i == 0:
                            e = self.g.add_edge(v2,v1)
                            self.vprop_size[v1] = self.node_size
                            self.edge_endpts.append(v1)
                            link.append(v1)
                            if 'oneway' not in tags:
                                self.eprop_marker[e] = 2
                        else:
                            e = self.g.add_edge(v1,v2)
                        
                        link.append(v2)
                        if ('oneway' in tags and tags['oneway'] == 'yes'):
                            self.eprop_thickness[e] = 0.25
                            if i == len(refs)-2:
                                self.eprop_marker[e] = 2
                        else:
			    self.eprop_thickness[e] = 0.75
			    self.eprop_marker[e] = 0
							
                        if self.vprop_size[v1] != self.node_size:
                            self.vprop_size[v1] = 0.0
                        if i==len(refs)-2:
                            self.vprop_size[v2] = self.node_size
                            self.edge_endpts.append(v2)
                        if self.vprop_size[v2] != self.node_size:
                            self.vprop_size[v2] = 0.0
                        self.vprop_fill_color[v1] = [0.640625, 0, 0, 0.9]
                        self.vprop_fill_color[v2] = [0.640625, 0, 0, 0.9]
                        self.vprop_shape[v1] = 0
                        self.vprop_shape[v2] = 0
                self.link_list.append(link)
                
    def node_data_extract(self, nodes):
        """After finding all higway nodes, get their lat and lng values"""
        for osm_id, lat, lng in nodes:
            if osm_id in self.highway_nodes:
                self.osm_to_graph[osm_id] = self.num_nodes
                self.g.add_vertex()
                self.vprop_pos[self.g.vertex(self.nodes)] = [lat,lng]
                self.nodes+=1

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='OSM map parser to output network in different formats')
    parser.add_argument('osm_filename', help='Name of the OSM file you want to parse')
    parser.add_argument('-d','--draw', help='Outputs an image of the map network')
    parser.add_argument('-o','--output', help='Output filename of network')
    parser.add_argument('-v','--vissim', help='Output file in VISSIM format')
    args = parser.parse_args()
  
    # Setup logging
   #if args.verbose:
    #    loglevel = logging.DEBUG
    #else:
    loglevel = logging.INFO
 
    main(args, loglevel)
