import subprocess
import sys
import networkx as nx
import os



def generate_config(edge,interval,suffix):
    config_filepath = '../config/config'+suffix+'.sumocfg'
    f = open(config_filepath,'w')
    lines = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">\n'
                    '<input>\n'
                            '<net-file value="../network/nyc.net.xml"/>\n'
                            '<route-files value="../trips/trip.xml"/>\n'
                            '<additional-files value="additional'+ suffix +'.xml"/>\n'
                    '</input>\n'
                    '<output>\n'
                            '<summary-output value="../output/summary'+ suffix + '.xml"/>\n'
                    '</output>\n'
                    '<report>\n'
                            '<log value="../output/report'+ suffix +'.xml"/>\n'
                    '</report>\n'
                    '</configuration>\n'
                    )
    f.write(lines)
    f.close()

def generate_additional(edge,interval,intervals,suffix):

    additional_filepath = '../config/additional'+suffix+'.xml'
    add_file = open(additional_filepath,'w')
    
    reroute_edges = ""
    for i,e in enumerate(edge[1]):
        if i == 0:
            reroute_edges += e
        else:
            reroute_edges += " " + e
        #reroute_edges += " " + str(e[0])+ 'to' + str(e[1])
    
    #Begin defining TAZ 
    taz = ''
    
    #Parsing destination edges
    destinations = []
    with open('../network/out_bridges.txt') as f:
        for line in f:
            if 'edge' in line:
                destinations.append(line[5:].rstrip())
                
    
    
    for i in range(21):
        with open('../network/zone'+str(i)+'.txt') as f:
            taz += '<taz id="zone'+str(i)+'">\n'
            for line in f:
                if 'edge' in line:
                    taz += '<tazSource id="' + line[5:].rstrip() + '"/>\n'
            taz += '<tazSink id="' + destinations[i] + '"/>\n'
            taz += '</taz>\n'
    #End defining TAZ

    lines = ('<additional>\n'
                            + taz + 
                            '<edgeData id="1" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[0][0]) + '" end="'+ str(intervals[0][1]) + '"/>\n'
                            '<edgeData id="2" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[1][0]) + '" end="'+ str(intervals[1][1]) + '"/>\n'
                            '<edgeData id="3" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[2][0]) + '" end="'+ str(intervals[2][1]) + '"/>\n'
                            '<edgeData id="4" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[2][1]) + '" end="100000"/>\n'
                    '<rerouter id="1" edges="'+ reroute_edges +'">\n'
                            '<interval begin="'+ str(interval[0]) +'" end="'+ str(interval[1]) +'">\n'
                                    '<closingReroute id="'+ edge[0] +'"/>\n' 
                                    '<destProbReroute id="'+ destinations[destinations.index(edge[0])-1] + '" probability="0.5"/>\n'
                                    '<destProbReroute id="'+ destinations[(destinations.index(edge[0])+1) % len(destinations)] + '" probability="0.5"/>\n'
                            '</interval>\n'
                    '</rerouter>\n'
                    '</additional>\n')
    add_file.write(lines)
    add_file.close()
    
        
def start():
    suffix = ""    
    vul_edges = {}        

    #Get vul_edges from rerouter folder
    for fn in os.listdir('../network/rerouters'):
        rerouters = []
        with open('../network/rerouters/'+fn) as f:
            for line in f:
                if 'edge' in line:
                    rerouters.append(line[5:].rstrip())
        vul_edges[fn[:-4]] = rerouters
                                     
    
    #dest_edges = ['4to5','3to5']
    intervals = [(0,5000),(5000,10000),(10000,15000)]
    for edge in vul_edges.items():
        for interval in intervals:
            if '--' in edge[0]:
                suffix = '_' + edge[0][2:] + '__' +str(interval[0]) + '_' +str(interval[1])
            else:
                suffix = '_' + edge[0] + '__' +str(interval[0]) + '_' +str(interval[1])
                
            generate_config(edge,interval,suffix)
            generate_additional(edge,interval,intervals,suffix)
            #print suffix +'\n'
            #sumoProcess = subprocess.Popen(['sumo',"--time-to-teleport","-1", "-c", "./config"+suffix+".sumocfg"], stdout=sys.stdout, stderr=sys.stderr)
            #sumoProcess.wait()
            #print "\n"
                    
if __name__=='__main__':
    start()
    print("Done")
