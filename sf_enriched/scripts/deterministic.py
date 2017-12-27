# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 13:54:47 2017

@author: Shekar
"""

#Run deterministic simulations
import sumolib
import subprocess
import sys

def generate_config(edge,interval,suffix):
    config_filepath = '../config/deterministic/config'+suffix+'.sumocfg'
    f = open(config_filepath,'w')
    lines = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">\n'
                    '<input>\n'
                            '<net-file value="../../network/SF_with_TLS.net.xml"/>\n'
                            '<route-files value="../../trips/trip.xml"/>\n'
                            '<additional-files value="additional'+ suffix +'.xml"/>\n'
                    '</input>\n'
                     '<processing>\n'
                        '<scale value="0.3"/>\n'
                    '</processing>\n'
                    '<output>\n'
                            '<summary-output value="../../output/summary'+ suffix + '.xml"/>\n'
                    '</output>\n'
                    '<report>\n'
                            '<log value="../../output/report'+ suffix +'.xml"/>\n'
                    '</report>\n'
                    '</configuration>\n'
                    )
    f.write(lines)
    
def generate_additional(edge,interval,suffix,intervals, rerouters):
    additional_filepath = '../config/deterministic/additional'+suffix+'.xml'
    f = open(additional_filepath,'w')
    lines = ('<additional>\n'
                    '<rerouter id="1" edges="'+ rerouters +'">\n'
                            '<interval begin="'+ str(interval[0]) +'" end="'+ str(interval[1]) +'">\n'
                                    '<closingReroute id="'+ edge.getID() +'"/>\n'
                            '</interval>\n'
                    '</rerouter>\n'
                    '</additional>\n')
    f.write(lines)
    
def start():
    suffix = ""
    network = sumolib.net.readNet('../network/SF_with_TLS.net.xml')
    vul_edges = network.getEdges()
    sumoBinary = 'sumo'
    intervals = [(0,28800),(28800,57600),(57600,86400)]
    rerouters = ""
    for edge in vul_edges:
        #if int(edge.getID().split('_')[0]) in [7, 8, 9]:
        if edge.getID() == '75_5':
            incoming = edge.getIncoming().keys()
            for e in incoming:
                rerouters += e.getID() + ' '
                for i in e.getIncoming().keys():
                    rerouters += i.getID() + ' '
                
            for interval in intervals:
                suffix = '_' + edge.getID() + '_' +str(interval[0]) + '_' + str(interval[1])
                generate_config(edge,interval,suffix)
                generate_additional(edge, interval, suffix, intervals, rerouters.strip())
                sumoProcess = subprocess.call([sumoBinary, "-c", "../config/deterministic/config"+suffix+".sumocfg"])
            
            
start()