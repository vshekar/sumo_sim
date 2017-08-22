from graph_tool.all import *
import os
import xml.etree.ElementTree as ET
import colorsys

list_file = os.listdir("./output")

def color_convert(maxd):
    red = 0.0
    green = 1.0
    RGB_list = []
    """
    while(red < 1.0):
        red += 2.0/maxd
        if (red > 1.0):
            red = 1.0
        RGB_list.append([red,green,0,1.0])
        
    while(green > 0):
        green -= 2.0/maxd
        if (green < 0.0):
            green =0.0
        RGB_list.append([red,green,0,1.0])
    """
    RGB_list = [[0.0,1.0,0.0],[1.0,1.0,0.0],[1.0,0.5,0.0],[1.0,0.0,0.0]]
    
    return RGB_list

if __name__=='__main__':
    g = Graph()
    
    edges = [(0,1),(1,0),(0,2),(2,0),(1,2),(1,3),(2,4),(4,2),(4,3),(3,4),(3,5),(5,3),(4,5)]
    pos = {0:(0,0),1:(800,-800),2:(800,800),3:(2000,-800),4:(2000,800),5:(2800,0)}
    vprop_pos = g.new_vertex_property("vector<double>")
    eprop_marker = [g.new_edge_property("double"),g.new_edge_property("double"),g.new_edge_property("double")]
    eprop_color = [g.new_edge_property("vector<double>"),g.new_edge_property("vector<double>"),g.new_edge_property("vector<double>")]
    eprop_thickness = [g.new_edge_property("double"),g.new_edge_property("double"),g.new_edge_property("double")]
    
    eprop_text = [g.new_edge_property("string"),g.new_edge_property("string"),g.new_edge_property("string")]
    
    
    #densities = [t1_density,t2_density,t3_density,t4_density]
    densities = [{} for i in range(4)]

    for fn in list_file:
        #if fn == 'edgeData_2to4__500_1000.xml':
        if fn == 'edgeData.xml':
            tree = ET.parse('./output/'+fn)
            root = tree.getroot()
            for i,interval in enumerate(root):
                print(i)
                for edge in interval:
                    if (edge.attrib['id'] != '-1to0' and edge.attrib['id'] != '5to-5') and ('density' in edge.attrib.keys()):
                        print(edge.attrib['id'] +  " : " + edge.attrib['density'])
                        densities[i][edge.attrib['id']] = float(edge.attrib['density'])
    
    t1_colors = [1.0 for i in range(len(edges))]
    
    for i in range(6):
        g.add_vertex()
        vprop_pos[i] = [pos[i][0],pos[i][1]]
    
     
    
    for edge in edges:
        e = g.add_edge(edge[0],edge[1])
        for i in range(3):
            
            #max_den = densities[i][max(densities[i])]
            max_den = densities[i][max(densities[i], key=densities[i].get)]
            print("max_den = " + str(max_den))
            RGB_list = color_convert(max_den)
            print(len(RGB_list))
            if str(edge[0])+'to'+str(edge[1]) in densities[i].keys():
                eprop_thickness[i][e] = densities[i][str(edge[0])+'to'+str(edge[1])]
                if eprop_thickness[i][e] > 15.0:
                    eprop_marker[i][e] = densities[i][str(edge[0])+'to'+str(edge[1])] * 2.5
                else:
                    eprop_marker[i][e] = 40.0

                eprop_text[i][e] = str(densities[i][str(edge[0])+'to'+str(edge[1])])
                #eprop_color[i][e] = color_convert(densities[i][str(edge[0])+'to'+str(edge[1])],max_den)
                print(densities[i][str(edge[0])+'to'+str(edge[1])])
                val = densities[i][str(edge[0])+'to'+str(edge[1])]/max_den
                if 1.0 >= val and val >0.75:
                    color = 3
                elif 0.75>= val and val > 0.5:
                    color = 2
                elif 0.5 >= val and val >= 0.25:
                    color = 1
                else:
                    color = 0
                eprop_color[i][e] = RGB_list[color]
                print(RGB_list[color])
            else:
                eprop_thickness[i][e] = 1.0
                eprop_text[i][e] = '0.0'
                eprop_color[i][e] = RGB_list[0]
                eprop_marker[i][e] = 40.0
    
    for i in range(3):
        graph_draw(g,vertex_text = g.vertex_index, vertex_font_size=50,vertex_fill_color='white',output_size=(1300,900),output="graph_t"+str(i+1)+".pdf",pos = vprop_pos,edge_marker_size=eprop_marker[i],vertex_size=45,edge_pen_width=eprop_thickness[i]  ,edge_text=eprop_text[i],edge_font_size=45,edge_color=eprop_color[i])
 


    
