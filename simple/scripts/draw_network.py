import networkx as nx
import matplotlib.pyplot as plt
import os
import xml.etree.ElementTree as ET

list_file = os.listdir("../output")

if __name__=='__main__':
    G = nx.DiGraph()
    G.add_nodes_from([x for x in range(6)])
    edges = [(0,1),(1,0),(0,2),(2,0),(1,2),(1,3),(2,4),(4,2),(4,3),(3,4),(3,5),(5,3),(4,5)]
    G.add_edges_from(edges)
    labels = {}
    pos = {0:(0,0),1:(800,600),2:(800,-600),3:(3000,600),4:(3000,-600),5:(2800,0)}
    t1_density = {}
    t2_density = {}
    t3_density = {}
    densities = [t1_density,t2_density,t3_density]

    for fn in list_file:
        if fn == 'edgeData.xml':
            tree = ET.parse('../output/'+fn)
            root = tree.getroot()
            for i,interval in enumerate(root):
                for edge in interval:
                    if (edge.attrib['id'] != '-1to0' and edge.attrib['id'] != '5to-5') and ('density' in edge.attrib.keys()):
                        print(edge.attrib['id'] +  " : " + edge.attrib['density'])
                        densities[i][edge.attrib['id']] = float(edge.attrib['density'])
                        
    t1_colors = [0.0 for i in range(len(edges))]
   
    for i,edge in enumerate(edges):
        G[edge[0]][edge[1]]['name'] = str(edge[0])+'to'+str(edge[1])
        if G[edge[0]][edge[1]]['name'] in t1_density.keys():
            t1_colors[i] = t1_density[G[edge[0]][edge[1]]['name']]

    for i in range(6):
        labels[i] = str(i)
        

            

    nx.draw(G,pos,node_size=1000, node_color='w',edge_color=t1_colors)
    nx.draw_networkx_labels(G,pos,labels,font_size=16)

    A = nx.nx_agraph.to_agraph(G)
    A.node_attr['shape']='circle'
    A.node_attr['fixedsize']='true'
    A.node_attr['fontsize']='22'
    A.node_attr['style']='filled'
    A.graph_attr['outputorder']='edgesfirst'
    A.graph_attr['label']="Simple Network"
    A.graph_attr['ratio']='1.0'
    #A.edge_attr['color']='#1100FF'
    A.edge_attr['style']='setlinewidth(2)'
    
    for i,node in enumerate(A.nodes()):
        print(pos[i])
        node.attr['pos'] = "%f,%f"%(pos[i][0],pos[i][1])
    
    print(A.node_attr)
    A.layout()
    A.draw("op.pdf")

    #plt.draw()
    #plt.show()
    print("Done")
