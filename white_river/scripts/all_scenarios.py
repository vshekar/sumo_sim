# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 16:07:28 2017

@author: Venkateswaran Shekar
"""

import traci
import traci.constants as tc
import sumolib
import math
import random
import xml.etree.ElementTree as ET

class SumoSim():
    SUMOBIN = "sumo-gui"
    SUMOCMD = [SUMOBIN, "-c", "../config/config.sumocfg", 
               "--ignore-route-errors", "true", "-W", "true", 
               "--time-to-teleport", "3600"]

    
    def __init__(self):
        #Initialize simulation
        self.flood_files = ['../Flood intersections/flood1.txt', 
                            '../Flood intersections/flood2.txt', 
                            '../Flood intersections/flood3.txt', 
                            '../Flood intersections/flood4.txt', 
                            '../Flood intersections/flood5.txt', 
                            '../Flood intersections/flood6.txt']
        self.network = sumolib.net.readNet('../wr_selected_new2.net.xml')
        self.edges = self.network.getEdges()
        traci.start(self.SUMOCMD)
        self.event_start = 3600*14 #Time at which event starts
        self.warning_time = 3600*6 #Warning x hours before event
        
        #Simulation stopping conditions
        self.arrived = 0
        self.total_vehicles = 500
        
        self.curr_trip = 0
        self.curr_veh = 0
        
        
        self.step = 0 #Keeps track of current sim time
        self.trips = self.get_trips()
        self.run_sim()
        traci.close()
        
    def get_trips(self):
        result = []
        tree = ET.parse('../trips/trip.xml')
        root = tree.getroot()
        for i, trip in enumerate(root):
            result.append((trip.attrib['from'], trip.attrib['to']))
        return result
        
        
    def run_sim(self):
        #while self.arrived < self.total_vehicles:
        self.evac_roads = list(reversed(self.get_evac_roads('staging')))
        #print(self.evac_roads)
        self.current_stage = 0
        while self.step < 24*3600:
            traci.simulationStep()
            self.step += 1
            self.arrived += traci.simulation.getArrivedNumber()
            
            #Evacuation or normal?
            if self.step >= self.warning_time:
                if self.step == self.warning_time + 500*(1+self.current_stage):
                    self.current_stage += 1
                self.evac_strat()
            else:
                self.normal_traffic()
                
            #Behavior of flood
            if self.step >= self.event_start:
                self.inundate()
                
    def evac_strat(self):
        if self.current_stage < len(self.evac_roads):
            print(self.current_stage)
            edges = self.evac_roads[self.current_stage]
            for edge in edges:
                 for i in range(1):
                     name = str(random.random())
                     traci.route.add(name, [edge[0].getID(), '-437502986'])
                     traci.vehicle.add(name, name, typeID="reroutingType")
        
    
    def normal_traffic(self):
        if self.gen_traffic():
            #print("In normal_traffic")
            self.curr_trip += 1
            trip = random.choice(self.trips)
            traci.route.add(str(self.curr_trip), [trip[0], trip[1]])
            traci.vehicle.add(str(self.curr_trip)+"veh", str(self.curr_trip), 
                              typeID="reroutingType")
                
    def inundate(self):
        pass
        
    
    def get_evac_roads(self, strat):
        evac_roads = []
        temp_evac_list = []
        dist = 5.0
        if strat == 'staging':
            x, y = 4195.27, 2874.88
        elif strat == 'river':
            x, y = 2073.12, 2404.40
            
        while len(temp_evac_list) < len(self.edges):
            stage = []
            edges = self.network.getNeighboringEdges(x, y, r=dist, includeJunctions=False)
            dist += 5.0
            for e in edges:
                if e not in temp_evac_list:
                    temp_evac_list.append(e)
                    stage.append(e)
            if len(stage) > 0:
                evac_roads.append(stage)
        return evac_roads
            
    def gen_traffic(self):
        if (
                (6*3600 <= self.step <= 12*3600) and 
                random.random() < self.pdf_6_to_12(self.step)
            ):
            #print("Morning Peak")
            return True
        elif (
                (15*3600 <= self.step <= 21*3600) and 
                random.random() < self.pdf_3_to_9(self.step)
              ):
            #print("Evening Peak")
            return True
        elif random.random() < 0.05:
            #print("Normal generation")
            return True
        else:
            return False
        
                
                
    def pdf_6_to_12(self,x):
        sigma=3000.0
        mu=9*3600
        t1 = (1/math.sqrt(2*math.pi*sigma**2))
        t2 = math.exp(-(x-mu)**2/(2*sigma**2))
        #return  t1*t2*6015.90785911
        return  t1*t2*3000
    
    def pdf_3_to_9(self,x):
        sigma=3000.0
        mu=18*3600
        t1 = (1/math.sqrt(2*math.pi*sigma**2))
        t2 = math.exp(-(x-mu)**2/(2*sigma**2))
        #return  t1*t2*6015.90785911 
        return  t1*t2*3000
        
    
if __name__=="__main__":
    s = SumoSim()
            