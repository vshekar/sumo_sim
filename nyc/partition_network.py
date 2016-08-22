import xml.etree.ElementTree as ET
import networkx as nx
#import metis

#This function generates an input file for metis
def start():
    fn = './network/nyc.net.xml'
    G,node_map = gen_graph(fn)
    op_file = './network/nyc_metis.txt'
    f = open(op_file,'w')
    f.writelines(str(nx.number_of_nodes(G))+' '+ str(nx.number_of_edges(G))+'\n')
    for i in range(1,nx.number_of_nodes(G)+1):
        st = ''
        for node in G.neighbors(i):
            st += str(node) + ' '
        f.writelines(st+'\n')
    f.close()

#This function assigns the edges to a zone as defined by the metis output file
def gen_zones():
    zone_fn = './network/zone'
    fn = './network/nyc.net.xml'
    G,node_map = gen_graph(fn)
    zone_list = []
    zones = [[] for i in range(21)]
    zones_fn = './network/nyc_metis.txt.part.21'
    for i,line in enumerate(open(zones_fn,'r')):
        zone_list.append(int(line))
        edges = nx.edges(G,i+1)
        for edge in edges:
            zones[int(line)].append(G.edge[edge[0]][edge[1]]['id'])
    
    for i,zone in enumerate(zones):
        f = open(zone_fn+str(i)+'.txt','w')
        for edge in zone:
            f.writelines('edge:'+edge+'\n')
        f.close()

#This function is used by gen_zones to create a networkx network
def gen_graph(fn):
    tree = ET.parse(fn)
    root = tree.getroot()
    G = nx.Graph()
    node_map = {}
    node_count = 1
    for el in root:
        if el.tag == 'edge' and 'function' not in el.attrib.keys():
            edge_id = el.attrib['id']
            start_node = el.attrib['from']
            end_node = el.attrib['to']
            if start_node not in node_map:
                node_map[start_node] = node_count
                node_count += 1 
            if end_node not in node_map:
                node_map[end_node] = node_count
                node_count += 1
            G.add_edge(node_map[start_node],node_map[end_node])
            G.edge[node_map[start_node]][node_map[end_node]]['id'] = edge_id
    #(edgecuts, parts) = metis.part_graph(G, 20)
    #for i,p in enumerate(edgecuts):
    #print G.nodes()
    return G,node_map
    


#start()
gen_zones()
