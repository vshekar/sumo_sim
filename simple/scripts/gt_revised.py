# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 11:32:17 2017

@author: shek628
"""
import traci
#import traci.constants as tc
import sumolib
#import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict


class SumoSim():
    SUMOBIN = "sumo"
    SUMOCMD = [SUMOBIN, "-c", "../config/config.cfg", "--ignore-route-errors",
               "true", "-W", "true", "--time-to-teleport", "-1", 
                "--weight-files", "../config/link_weights.xml", 
                "--weight-attribute", "traveltime"]

    def __init__(self, prev_rho, prev_gamma, prev_tau):
        
        self.prev_rho = prev_rho
        self.prev_gamma = prev_gamma
        self.prev_tau = prev_tau
                
        self.network = sumolib.net.readNet('../network/simple.net.xml')
        self.edges = [e for e in self.network.getEdges() 
                        if (e.getID() != '-1to0' and e.getID() != '5to-5')]
        self.delta = 500
        
        self.tau = pd.DataFrame()
        self.gamma = pd.DataFrame()
        self.rho = pd.DataFrame()
        
        self.densities = defaultdict(float)
        
        self.total_vehicles = 500
        
        traci.start(self.SUMOCMD)
        for edge in self.edges:
            traci.edge.subscribe(edge.getID(), varIDs=(16,96), begin=0, 
                                 end=86400000)
        
        self.run_sim()
        
    def run_sim(self):
        self.arrived = 0
        self.step = 0
        while self.arrived < self.total_vehicles:
            vehIDs = traci.edge.getLastStepVehicleIDs('-1to0')
            for id in vehIDs:
                traci.vehicle.rerouteTraveltime(id, currentTravelTimes=False)
                traci.simulationStep()
                self.step += 1
                self.arrived += traci.simulation.getArrivedNumber()
                self.calc_density()
                
                if ((self.step % self.delta == 0) 
                    or (self.arrived == self.total_vehicles)):
                    self.aggregate()
                    

        traci.close()         
        
    def aggregate(self):
        t = {}
        g = {}
        r = {}
        interval_num = int(self.step/self.delta)
        if type(self.prev_tau) != type(None):
            
            rho_denom = 0
            for edge in self.edges:
                edge_id = edge.getID()
                prev_rho = self.prev_rho.iloc[interval_num][edge_id]
                prev_tau = self.prev_tau.iloc[interval_num][edge_id]
                                
                fft = edge.getLength()/edge.getSpeed()
                s = ((1 - prev_rho) * fft) + (prev_rho * len(self.edges) * fft)
                t[edge_id] = ((1/self.iteration) * s + (1-1/self.iteration)
                                    * prev_tau)
                self.increase_len(edge_id, t[edge_id])
                
                g[edge_id] = self.densities[edge_id]/self.delta
                rho_denom += g[edge_id] * prev_tau
            
            for edge in self.edges:
                edge_id = edge.getID()
                r[edge_id] = (g[edge_id] * prev_tau) / rho_denom
        else:
            for edge in self.edges():
                el = edge.getLength()
                sp = edge.getSpeed()
                edge_id = edge.getID()
                t[edge_id] = el/sp
                g[edge_id] = 0
                r[edge_id] = 1/len(self.edges)
        self.densities = defaultdict(float)
        self.tau = self.tau.append(t, ignore_index = True)
        self.gamma = self.gamma.append(g, ignore_index = True)
        self.rho = self.rho.append(r, ignore_index = True)        
          
    def calc_density(self):
        temp_densities = {}
        temp_total_density = 0
        for edge in self.edges:
            res = traci.edge.getSubscriptionResults(edge.getID())
            if res != None:
                #self.densities[edge.getID()] += res[16]/edge.getLength()
                #self.total_density += res[16]/edge.getLength()
                temp_densities[edge.getID()] = res[16]
                temp_total_density += res[16]
        
        for edge in self.edges:
            if temp_total_density > 0:
                self.densities[edge.getID()] +=  temp_densities[edge.getID()]/temp_total_density
            else:
                self.densities[edge.getID()] = 0
                
    def increase_len(self, edgeID, len):
        traci.edge.setEffort(edgeID, len)
        traci.edge.adaptTraveltime(edgeID, len)


if __name__ == "__main__":
    network = sumolib.net.readNet('../network/simple.net.xml')
    edges = [e for e in network.getEdges() if (e.getID() != '-1to0' and e.getID() != '5to-5')]
    sim_time = pd.DataFrame()
    for i in range(345):
        t = {}
        for edge in edges:
            s = SumoSim(edge.getID(), i, edges)
            t[edge.getID()] = s.step
        sim_time = sim_time.append(t, ignore_index=True)
        sim_time.to_csv('sim_time.csv')
