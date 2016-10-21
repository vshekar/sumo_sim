import xml.etree.ElementTree as ET


def chunk_gen(lst, n):
    n = len(lst)/n
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def write_zone(lst,i):
    f = open('../network/zone'+str(i)+'.txt','w')
    for link in lst:
        f.write('junction:'+link+'\n')
    f.close()

def get_sources2():
    fn = '../network/nyc.net.xml'
    tree = ET.parse(fn)
    root = tree.getroot()
    prev_id = "None"
    sources = []
    for el in root:
        if el.tag == 'junction' and 'function' not in el.attrib.keys() and 'shape' in el.attrib.keys():
            sources.append(el.attrib['id'])
    link_lists = chunk_gen(sources, 20)
    for i in range(20):
        write_zone(next(link_lists),i)

def get_sources():
    sources = []
    f = open('../network/Test_manhattan.txt','r')
    for line in f.readlines():
        if 'edge' in line:
            sources.append(line[5:])
    #print(len(sources))
    #print sources[-1]
    link_lists = chunk_gen(sources, 20)
    for i in range(20):
        write_zone(next(link_lists),i)

#This is a temp function to remove links in zone files that are not present in the network. Valid links are described in         
def clean_zones():
    zone_fn = '../network/zone'
    bridge_fn = '../network/select.txtcomp0.txt'
    bridges = []


    with open(bridge_fn,'r') as f:
        for line in f:
            bridges.append(line)

    for i in range(20):
        temp_list = []
        with open(zone_fn+str(i)+'.txt','r') as f:
            for line in f:
                if line in bridges:
                    temp_list.append(line)

        with open(zone_fn+str(i)+'.txt','w') as f:
            for line in temp_list:
                f.writelines(line)
    print("Complete")

clean_zones()