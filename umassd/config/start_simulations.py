#!/usr/bin/env python
import subprocess
import sys
import networkx as nx



def generate_config(edge,interval,suffix):
    config_filepath = './config'+suffix+'.sumocfg'
    f = open(config_filepath,'w')
    lines = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">\n'
                    '<input>\n'
                            '<net-file value="../network/umassd.net.xml"/>\n'
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

def generate_additional(edge,G,interval,intervals,suffix):
    additional_filepath = './additional'+suffix+'.xml'
    f = open(additional_filepath,'w')
    
    reroute_edges = ""
    for i,e in enumerate(edge[1]):
        if i == 0:
            reroute_edges += e
        else:
            reroute_edges += " " + e
    """
    for ed in G.edges_iter():
        if G[ed[0]][ed[1]]['name'] == edge:
            #print "Found it!"
            for i,e in enumerate(G.in_edges(ed[0])):
                if i== 0:
                    reroute_edges += str(e[0])+ 'to' + str(e[1])
                else:
                    reroute_edges += " " + str(e[0])+ 'to' + str(e[1])
    """
	
    lines = ('<additional>\n'
                            '<taz id="source">\n'
                                    '<tazSource id="--12805"/>\n'
                                    '<tazSource id="-12790"/>\n'
                                    '<tazSource id="-12811"/>\n'
                                    '<tazSource id="-12808"/>\n'
                                    '<tazSource id="-12797"/>\n'
                                    '<tazSource id="--12816"/>\n'
                                    '<tazSource id="-12798"/>\n'
                                    '<tazSource id="-12804"/>\n'
                                    '<tazSource id="--12814#11"/>\n'
                                    '<tazSource id="--12786#0"/>\n'
                                    '<tazSink id="-12826"/>\n'
                            '</taz>\n'
                            '<edgeData id="1" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[0][0]) + '" end="'+ str(intervals[0][1]) + '"/>\n'
                            '<edgeData id="2" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[1][0]) + '" end="'+ str(intervals[1][1]) + '"/>\n'
                            '<edgeData id="3" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[2][0]) + '" end="'+ str(intervals[2][1]) + '"/>\n'
                            '<edgeData id="4" file="../output/edgeData'+ suffix +'.xml" begin="'+ str(intervals[2][1]) + '" end="10000"/>\n'
                    '<rerouter id="1" edges="'+ reroute_edges +'">\n'
                            '<interval begin="'+ str(interval[0]) +'" end="'+ str(interval[1]) +'">\n'
                                    '<closingReroute id="'+ edge[0] +'"/>\n' 
                            '</interval>\n'
                    '</rerouter>\n'
                    '</additional>\n')
    f.write(lines)
    
    
    
def start(G):
    suffix = ""
    #vul_edges = ['4to5','3to5','3to4','1to3','2to4','1to2','0to1','0to2']
    vul_edges = {'--12814#1':['--12805','--12814#2'],'--12814#2':['-12790','--12814#3'],'--12814#3':['-12811','--12814#4'],'--12814#4':['--12814#5','--12821'],'--12814#6':['--12814#7','-12801#1'],'--12814#7':['-12797','--12814#8'],'--12814#9':['-12804','--12814#10'],'--12814#10':['-12782','--12814#11'],'-12814#13':['-12770','-12814#12'],'-12814#14':['--12786#0','-12814#13'],'-12814#15':['--12816','-12814#14'],'-12814#16':['-12798','-12814#15']}
    #dest_edges = ['4to5','3to5']
    intervals = [(0,3000),(3000,6000),(6000,9000)]
    for edge in vul_edges.items():
        for interval in intervals:
            if edge[0][:2] == '--':
                suffix = '_' + edge[0][2:] + '__' +str(interval[0]) + '_' +str(interval[1])
            else:
                suffix = '_' + edge[0] + '__' +str(interval[0]) + '_' +str(interval[1])
            generate_config(edge,interval,suffix)
            generate_additional(edge,G,interval,intervals,suffix)
            #print suffix +'\n'
            sumoProcess = subprocess.Popen(['sumo',"--time-to-teleport","-1", "-c", "./config"+suffix+".sumocfg"], stdout=sys.stdout, stderr=sys.stderr)
            sumoProcess.wait()
            #print "\n"
                    
if __name__=='__main__':
    G = nx.DiGraph()
    G.add_nodes_from([x for x in range(6)])
    edges = [(-1,0),(0,1),(1,0),(0,2),(2,0),(1,2),(1,3),(2,4),(4,2),(4,3),(3,4),(3,5),(5,3),(4,5)]
    G.add_edges_from(edges)
    for edge in edges:
        G[edge[0]][edge[1]]['name'] = str(edge[0])+'to'+str(edge[1])
    start(G)
    print("Done")
