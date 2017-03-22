import xml.etree.ElementTree as ET
from graph_tool.all import *

def parse_weights():
    #fn = './output/edgeData.xml'
    fn = './output/edgeData_--12814#1__6000_9000.xml'
    tree = ET.parse(fn)
    root = tree.getroot()
    densities = [{} for i in range(4)]
    for i,interval in enumerate(root):
        #print i
        for edge in interval:
            
            if 'density' in edge.attrib.keys():
                densities[i][edge.attrib['id']] = float(edge.attrib['density'])
            else:
                densities[i][edge.attrib['id']] = 1.0
    return densities


def gen_graph():
    
    den = parse_weights()
    g = Graph()
    v_pos = g.new_vertex_property("vector<double>")
    v_name = g.new_vertex_property("string")
    v_size = g.new_vertex_property("double")

    e_marker = g.new_edge_property("double")
    e_name = g.new_edge_property("string")
    e_weight = [g.new_edge_property("double") for i in range(len(den))]
    e_color = [g.new_edge_property("vector<double>") for i in range(len(den))]
    e_label = [g.new_edge_property("string") for i in range(len(den))]
    for x,densities in enumerate(den):
        #print x
        fn = './network/umassd.net.xml'

        tree = ET.parse(fn)
        root = tree.getroot()

        
        
        prev_id = "None"
        for el in root:
            if el.tag == 'edge' and 'function' not in el.attrib.keys() and 'shape' in el.attrib.keys():
                edge_id = el.attrib['id']
                start_node = el.attrib['from']
                end_node = el.attrib['to']
                pos_list = el.attrib['shape'].split()
                last_vertex = len(pos_list)
                for i,pos in enumerate(pos_list):
                    pos = pos.split(',')
                    v = g.add_vertex()
                    v_pos[v] = [float(pos[1]),float(pos[0])]
                    if i == 0:
                        v_size[v] = 1.0
                        v_name[v] = start_node
                        prev_vertex = v
                    elif i == last_vertex:
                        v_size[v] = 1.0
                        v_name[v] = end_node
                    else:
                        v_size[v] = 0.0
                    if i >0:
                        e = g.add_edge(prev_vertex,v)
                        prev_vertex = v
                        e_marker[e] = 0.0
                        e_name[e] = edge_id
                        if edge_id in densities.keys() and "12814" in el.attrib['id']:
                            e_weight[x][e] = densities[edge_id]*0.1
                        else:
                            e_weight[x][e] = 1.0
        
        max_wt = max(e_weight[x])*10
        RGB_list = [[0.0,1.0,0.0,1.0],[1.0,1.0,0.0,1.0],[1.0,0.5,0.0,1.0],[1.0,0.0,0.0,1.0]]
        #for i,wt in enumerate(e_weight):
        prev_wt = 1.0
        counter = 0
        for i,edge in enumerate(g.edges()):
            wt = e_weight[x][edge]
            #if e_name[edge].split('#')[0] != prev_id.split('#')[0]:
            
            if wt != prev_wt and wt*10 > 1.0:
                e_label[x][edge] = str(wt*10)
                counter = 0
            else:
                counter += 1
                
            prev_wt = wt 
            
            if wt == 1.0:
                e_color[x][edge] = RGB_list[0]
            else:
                val = wt*10/max_wt
                if 1.0 >= val and val >0.75:
                    color = 3
                elif 0.75>= val and val > 0.5:
                    color = 2
                elif 0.5 >= val and val >= 0.25:
                    color = 1
                else:
                    color = 0
                #print color
                e_color[x][edge] = RGB_list[color]
                
    for i in range(4):
        graph_draw(g,pos=v_pos,vertex_size=v_size,edge_end_marker=e_marker,edge_pen_width=e_weight[i],fit_view=True,output_size=(800,800),edge_color=e_color[i],edge_text=e_label[i],edge_font_size=3,edge_text_distance=10,output='umassd_S1_t3_'+str(i)+'.pdf')
        #graph_draw(g,pos=v_pos,vertex_size=v_size,edge_end_marker=e_marker,edge_pen_width=e_weight[i],fit_view=True,output_size=(800,800),edge_color=e_color[i],edge_text=e_label[i],edge_font_size=3,edge_text_distance=10,output='umassd_nominal_'+str(i)+'.pdf')
gen_graph()
