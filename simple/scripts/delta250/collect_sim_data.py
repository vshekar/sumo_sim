# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 05:13:37 2017

@author: Shekar
"""

import pandas as pd
import traci
import sumolib
from collections import defaultdict
import scipy.stats
import matplotlib.pyplot as plt
import math
from traci.exceptions import FatalTraCIError


class SumoSim():
    SUMOBIN = "sumo-gui"
    SUMOCMD = [SUMOBIN, "-c", "../../config/config.cfg", "--time-to-teleport", "-1"]
    
    def __init__(self):
        self.network = sumolib.net.readNet('../../network/simple.net.xml')
        self.edges = [e for e in self.network.getEdges() if 
                      (e.getID() != '-1to0' and e.getID() != '5to-5')]
        
        self.delta = 250
        self.travel_times = {}
        
        self.run_sim()
        self.total_intervals = math.ceil(self.step/self.delta)
        for interval in range(self.total_intervals):
            for edge in self.edges:
                self.run_sim(disabled_edge=edge.getID(), disabled_interval=interval)
        
    def run_sim(self, disabled_edge = None, disabled_interval = None):
        traci.start(self.SUMOCMD)
        self.step = 0
        self.arrived = 0
        if disabled_edge != None and disabled_interval != None:
            print('Disabled case')
            while(self.arrived < 500):
                if (self.step%self.delta ==0 and 
                    math.ceil(self.step/self.delta) == disabled_interval):
                    edge = self.network.getEdge(disabled_edge)
                    for lane in edge.getLanes():
                        traci.lane.setDisallowed(lane.getID(),['passenger'])
                if((self.step%self.delta) == 0 and
                    math.ceil(self.step/self.delta) == disabled_interval +1):
                    for lane in edge.getLanes():
                        traci.lane.setDisallowed(lane.getID(), [])
                traci.simulationStep()
                self.step += 1
                self.arrived += traci.simulation.getArrivedNumber()
                
                            
            self.travel_times[disabled_edge+str(disabled_interval)]  = self.step
        else:
            print('Nominal case')
            while(self.arrived < 500):
                traci.simulationStep()
                self.step += 1
                self.arrived += traci.simulation.getArrivedNumber()
            self.travel_times['Nominal'] = self.step
        traci.close()
        
if __name__ == "__main__":
    s = SumoSim()
    print(s.travel_times)