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
import population

class SumoSim():
    SUMOBIN = "sumo"
    SUMOCMD = [SUMOBIN, "-c", "../config/config.sumocfg", 
               "--ignore-route-errors", "true", "-W", "true", 
               "--time-to-teleport", "-1"]

    
    def __init__(self, event_start=12, warning_time=10, inundation_rate=1, strat='staging', evac_roads=None):
        #Initialize simulation
        self.flood_files = ['../Flood intersections/flood1.txt', 
                            '../Flood intersections/flood2.txt', 
                            '../Flood intersections/flood3.txt', 
                            '../Flood intersections/flood4.txt', 
                            '../Flood intersections/flood5.txt', 
                            '../Flood intersections/flood6.txt']
        self.network = sumolib.net.readNet('../wr_selected_new.net.xml')
        self.edges = self.network.getEdges()
        
        self.event_start = 3600*event_start #Time at which event starts
        self.warning_time = 3600*warning_time #Warning at time=x
        self.inundation_rate = 3600*inundation_rate
        self.strat = strat
        if evac_roads == None:
            self.evac_roads = list(self.get_evac_roads(self.strat))
        else:
            self.evac_roads = evac_roads
        
        self.travel_times = {}
        self.start_times = {}
        
        #Simulation stopping conditions
        self.arrived = 0
        self.departed = 0
        self.simulation_running = True
        
        self.curr_trip = 0
        self.curr_veh = 0
        
        #
        self.population = population.random_pop()
        self.file_count = 0
        
        self.step = 0 #Keeps track of current sim time
        self.trips = self.get_trips()
        #self.run_sim()
        #self.end_simulation()
        
    def get_trips(self):
        result = []
        tree = ET.parse('../trips/trip.xml')
        root = tree.getroot()
        for i, trip in enumerate(root):
            result.append((trip.attrib['from'], trip.attrib['to']))
        return result
        
        
    def run_sim(self):
        #while self.arrived < self.total_vehicles:
        traci.start(self.SUMOCMD)
        #print(self.evac_roads)
        self.current_stage = 0
        #while self.step < 24*3600:
        while self.simulation_running:
            traci.simulationStep()
            self.step += 1
            
            #Record number of vehicles in the network at the time of warning
            self.total_normal_traffic = 0
            if self.step == self.warning_time:
                for edge in self.edges:
                    edgeID = edge.getID()
                    self.total_normal_traffic += traci.edge.getLastStepVehicleNumber(edgeID)
            
            #Evacuation or normal?
            if self.step >= self.warning_time:
                if self.step == self.warning_time + 500*(1+self.current_stage):
                    #print(self.evac_roads[self.current_stage])
                    self.current_stage += 1
                self.evac_strat()
            else:
                self.normal_traffic()
                
            #Behavior of flood
            if self.step >= self.event_start:
                self.inundate()
                
    def evac_strat(self):
        if self.current_stage < len(self.evac_roads):
            self.arrived += traci.simulation.getArrivedNumber()
            self.departed += traci.simulation.getDepartedNumber()
            
            for veh in traci.simulation.getDepartedIDList():
                self.start_times[veh] = self.step
            
            for veh in traci.simulation.getArrivedIDList():
                if veh in self.start_times.keys():
                    self.travel_times[veh] = self.step - self.start_times[veh]
            
            edges = self.evac_roads[self.current_stage]
            for edge in edges:
                e = edge[0].getID()               
                if self.population[e] != 0:
                    self.population[e] -= 1
                    name = str(random.random())
                    traci.route.add(name, [e, '-437502986'])
                    try:
                        traci.vehicle.add(name, name, typeID="reroutingType")
                    except traci.TraCIException:
                        self.departed += 1
                        #print(e)
        elif self.current_stage == len(self.evac_roads):
            stop_simulation = True
            for edge in self.edges:
                edgeID = edge.getID()
                for veh in traci.edge.getLastStepVehicleIDs(edgeID):
                    if traci.vehicle.getWaitingTime(veh) == 0:
                        stop_simulation = False
                        break

                    
            if stop_simulation:                    
                self.end_simulation()
    
    
    def end_simulation(self):
        """
        print('Warning Time : {}'.format(self.warning_time/3600))
        print('Event Time : {}'.format(self.event_start/3600))
        print('Simulation End: {}'.format(self.step/3600))
        print('Departed = {}'.format(self.departed))
        print('Departed - Arrived = {}'.format(self.departed - self.arrived))
        """
        avg_travel = sum(self.travel_times.values())/len(self.travel_times.keys())
        max_travel = max(self.travel_times.values())
        print('{}, {}, {:.4f}, {:.4f}, {}, {:.4f}'.format(self.warning_time/3600, 
              self.event_start/3600, self.step/3600, 
              ((self.arrived-self.total_normal_traffic)/self.departed)*100, 
                 max_travel, avg_travel))
        
        traci.close()
        self.simulation_running = False
    
    def normal_traffic(self):
        if self.gen_traffic():
            #print("In normal_traffic")
            self.curr_trip += 1
            trip = random.choice(self.trips)
            traci.route.add(str(self.curr_trip), [trip[0], trip[1]])
            try:
                traci.vehicle.add(str(self.curr_trip)+"veh", 
                                  str(self.curr_trip), typeID="reroutingType")
            except:
                print(trip)
    
    
    def inundate(self):
        if self.step%(self.inundation_rate) == 0:
                self.disable_links(self.file_count)
                self.file_count += 1
                #Reroute every vehicle in the simulation
                for edge in self.edges:
                        vehIDs = traci.edge.getLastStepVehicleIDs(edge.getID())
                        for id in vehIDs:
                            traci.vehicle.rerouteTraveltime(id,
                                                    currentTravelTimes=True)
                
    def disable_links(self, count=0):
        f = open(self.flood_files[count],'r')
        self.origIDs = []
        for l in f:
            self.origIDs.append(l.rstrip())
            
        self.disabled_edges = []

        for l in self.origIDs:
            for edge in self.network.getEdges():
                if l in edge.getID():
                    self.disabled_edges.append(edge)
                    for lane in edge.getLanes():
                        traci.lane.setDisallowed(lane.getID(),['passenger'])
                
        
    
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
            edges = self.network.getNeighboringEdges(x, y, r=dist, 
                                                     includeJunctions=False)
            dist += 5.0
            for e in edges:
                if e not in temp_evac_list:
                    temp_evac_list.append(e)
                    stage.append(e)
            if len(stage) > 0:
                evac_roads.append(stage)
                
        if strat == 'staging':
            evac_roads = reversed(evac_roads)
        elif strat == 'river':
            evac_roads = evac_roads
        
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
    #evac_roads = list(s.get_evac_roads('staging'))
    evac_roads = None
    s = SumoSim(event_start=11, warning_time=10, inundation_rate=1, strat='staging')
    s.run_sim()
    s = SumoSim(event_start=11, warning_time=9, inundation_rate=1, strat='staging')
    s.run_sim()
    s = SumoSim(event_start=11, warning_time=8, inundation_rate=1, strat='staging')
    s.run_sim()
    s = SumoSim(event_start=11, warning_time=7, inundation_rate=1, strat='staging')
    s.run_sim()
    s = SumoSim(event_start=11, warning_time=6, inundation_rate=1, strat='staging')
    s.run_sim()
    s = SumoSim(event_start=11, warning_time=5, inundation_rate=1, strat='staging')
    s.run_sim()