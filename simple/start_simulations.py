#!/usr/bin/env python
import subprocess
import sys

def generate_config(edge,interval,suffix):
    config_filepath = './config'+suffix+'.sumocfg'
    f = open(config_filepath,'w')
    lines = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">\n'
                    '<input>\n'
                            '<net-file value="../network/simple.net.xml"/>\n'
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

def generate_additional(edge,interval,suffix,intervals):
    additional_filepath = './config/additional'+suffix+'.xml'
    f = open(additional_filepath,'w')
    lines = ('<additional>\n'
                            '<taz id="source">\n'
                                    '<tazSource id="0to1"/>\n'
                                    '<tazSource id="0to2"/>\n'
                                    '<tazSink id="4to5"/>\n'
                                    '<tazSink id="3to5"/>\n'
                            '</taz>\n'
                            '<edgeData id="1" file="../output/edgeData'+ suffix +'.xml" begin="'+str(intervals[0][0]) +'" end="'+str(intervals[0][1]) +'"/>\n'
                            '<edgeData id="2" file="../output/edgeData'+ suffix +'.xml" begin="'+str(intervals[1][0]) +'" end="'+str(intervals[1][1]) +'"/>\n'
                            '<edgeData id="3" file="../output/edgeData'+ suffix +'.xml" begin="'+str(intervals[2][0]) +'" end="'+str(intervals[2][1]) +'"/>\n'
                            '<edgeData id="4" file="../output/edgeData'+ suffix +'.xml" begin="'+str(intervals[2][1]) +'" end="100000"/>\n'
                    '<rerouter id="1" edges="0to1 0to2">\n'
                            '<interval begin="'+ str(interval[0]) +'" end="'+ str(interval[0]) +'">\n'
                                    '<closingReroute id="'+ edge +'"/>\n'
                            '</interval>\n'
                    '</rerouter>\n'
                    '</additional>\n')
    f.write(lines)

def start():
    suffix = ""
    vul_edges = ['4to5','3to5','3to4','1to3','2to4','1to2']
    #intervals = [(0,1000),(1000,2000),(2000,20000)]
    intervals = [(0,500),(500,1000),(1000,1500)]
    for edge in vul_edges:
        for interval in intervals:
            suffix = '_' + edge + '_' +str(interval)
            generate_config(edge,interval,suffix)
            generate_additional(edge,interval,suffix,intervals)
            sumoProcess = subprocess.Popen([sumoBinary, "-c", "./config"+suffix+".sumocfg"], stdout=sys.stdout, stderr=sys.stderr)
            sumoProcess.wait()
start()
