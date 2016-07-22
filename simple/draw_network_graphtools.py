from graph_tool.all import *
import os
import xml.etree.ElementTree as ET


list_file = os.listdir("./output")

if __name__=='__main__':
    g = Graph()
    
    edges = [(0,1),(1,0),(0,2),(2,0),(1,2),(1,3),(2,4),(4,2),(4,3),(3,4),(3,5),(5,3),(4,5)]
    pos = {0:(0,0),1:(800,-800),2:(800,800),3:(2000,-800),4:(2000,800),5:(2800,0)}
    vprop_pos = g.new_vertex_property("vector<double>")
    eprop_marker = g.new_edge_property("double")
    eprop_thickness = [g.new_edge_property("double"),g.new_edge_property("double"),g.new_edge_property("double")]
    
    eprop_text = [g.new_edge_property("string"),g.new_edge_property("string"),g.new_edge_property("string")]
    
    t1_density = {}
    t2_density = {}
    t3_density = {}
    densities = [t1_density,t2_density,t3_density]

    for fn in list_file:
        if fn == 'edgeData_2to4__500_1000.xml':
        #if fn == 'edgeData.xml':
            tree = ET.parse('./output/'+fn)
            root = tree.getroot()
            for i,interval in enumerate(root):
                for edge in interval:
                    if (edge.attrib['id'] != '-1to0' and edge.attrib['id'] != '5to-5') and ('density' in edge.attrib.keys()):
                        print edge.attrib['id'] +  " : " + edge.attrib['density']
                        densities[i][edge.attrib['id']] = float(edge.attrib['density'])
    
    t1_colors = [1.0 for i in range(len(edges))]
    
    for i in range(6):
        g.add_vertex()
        vprop_pos[i] = [pos[i][0],pos[i][1]]
    
    for edge in edges:
        e = g.add_edge(edge[0],edge[1])
        for i in range(3):
            if str(edge[0])+'to'+str(edge[1]) in densities[i].keys():
                eprop_thickness[i][e] = densities[i][str(edge[0])+'to'+str(edge[1])]
                eprop_text[i][e] = str(densities[i][str(edge[0])+'to'+str(edge[1])])
            else:
                eprop_thickness[i][e] = 1.0
                eprop_text[i][e] = '0.0'
    
    for i in range(3):
        graph_draw(g,vertex_text = g.vertex_index, vertex_font_size=18,vertex_fill_color='white',output_size=(1400,800),output="graph_2to4_"+str(i)+".pdf",pos = vprop_pos,edge_marker_size=40,vertex_size=45,edge_pen_width=3.0,edge_text=eprop_text[i],edge_font_size=24)
 


    
