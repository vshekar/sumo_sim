# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 13:49:43 2017

@author: Shekar
"""

import traci
import sumolib
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

class SumoSim():
    SUMOBIN = "sumo-gui"
    SUMOCMD = [SUMOBIN, "-c", "../config/config.sumocfg", "--ignore-route-errors", "true", "-W", "true", "--time-to-teleport", "-1"]


    def __init__(self, start_interval=None, end_interval=None, disabled_link=None):
        #Initialize simulation
        self.start_interval = start_interval
        self.end_interval = end_interval
        
        self.network = sumolib.net.readNet('../network/umassd.net.xml')
        traci.start(self.SUMOCMD)
        self.edges = [e for e in self.network.getEdges()]
        self.total_vehicles = 4000
        
        self.disabled_link = disabled_link
        self.disabled_lanes = []
        traci.simulation.subscribe(varIDs=(122,121))
        #traci.vehicle.subscribe(varIDs=(90))
        for edge in self.edges:
            edgeID = edge.getID()
            traci.edge.subscribe(edgeID, varIDs=(96,101,16))
            #if self.disabled_link == :
        
        edge = self.network.getEdge(self.disabled_link)    
        for lane in edge.getLanes():
            self.disabled_lanes.append(lane)
        
        self.run_sim()
        traci.close()
        
    def reroute(self):
        veh_ids = []                    
        for edge in self.edges:
            veh_ids = traci.edge.getLastStepVehicleIDs(edge.getID()) + veh_ids
        for veh_id in veh_ids:
            traci.vehicle.rerouteTraveltime(veh_id)    

    def run_sim(self):
        self.step = 0
        self.arrived = 0
        self.CO2_vals = []
        self.fuel_vals = []
        while self.arrived < self.total_vehicles:
            #if self.step%1000 == 0:
                traci.simulationStep()
                total_CO2 = 0
                total_fuel = 0
                for edge in self.edges:
                    edge_ID = edge.getID()
                    res = traci.edge.getSubscriptionResults(edge_ID)
                    total_CO2 += res[96]
                    total_fuel += res[101]
                    
                    #total_CO2 += traci.edge.getCO2Emission(edge_ID)
                    #total_fuel += traci.edge.getFuelConsumption(edge_ID)
                self.CO2_vals.append(total_CO2)
                self.fuel_vals.append(total_fuel)
                #self.CO2_vals[self.step] = total_CO2
                #self.fuel_vals[self.step] = total_fuel
                if (self.start_interval!=None and self.start_interval == self.step):
                    for lane in self.disabled_lanes:
                        #traci.lane.setMaxSpeed(lane.getID(),0)
                        traci.lane.setDisallowed(lane.getID() ,['passenger'])
                    self.reroute()                    
        
                if (self.end_interval!=None and self.end_interval == self.step):
                    for lane in self.disabled_lanes:
                        traci.lane.setDisallowed(lane.getID(),[])
                        #traci.lane.setMaxSpeed(lane.getID(),13.4112)
                    self.reroute()
                
                res = traci.simulation.getSubscriptionResults()
                #self.arrived += traci.simulation.getArrivedNumber()
                self.arrived += res[121]
                self.step += 1
        
        #sns.set(font_scale=1.5)
        #sns.set_style("darkgrid")
        #f, (ax) = plt.subplots(1, 1, sharex=False)   
        #plt.plot(self.CO2_vals)
        #plt.legend(bbox_to_anchor=(.05, 1), loc=2, borderaxespad=0.)
        #ax.set_ylabel('$CO_{2}$ released (Kg)')
        #ax2.set_ylabel('Fuel consumed (Liters)')
        #ax.set_xlabel('Time (seconds)')
        #op = pd.DataFrame({'CO2': self.CO2_vals, 'Fuel': self.fuel_vals})
        #op.to_csv('disrupted_{}_{}_{}.csv'.format(self.start_interval, self.end_interval, self.disabled_link))
        
if __name__=="__main__":
    #s = SumoSim(0, 3000, '--12814#1')
    #s = SumoSim(3000, 6000, '--12814#1')
    #s = SumoSim(6000, 9000, '--12814#1')
    #links = {'S1':'--12814#1', 'S2':'--12814#2', 'S3':'--12814#3', 
    #         'S4':'--12814#4', 'S5':'--12814#6', 'S6':'--12814#7',
    #         'S7':'--12814#9', 'S8':'--12814#10', 'S9':'-12814#13',
    #         'S10':'-12814#14', 'S11':'-12814#15', 'S12':'-12814#16'}
    links = {'S7':'--12814#9'}
    op = pd.DataFrame(columns=('Scenario', 'Delta', 'Travel Time'))
    count = 0
    #s = SumoSim()
    #op.loc[count] = ['Nominal', 'None', s.step]
    #count += 1
    for l in links.keys():
        s = SumoSim(0, 3000, links[l])
        op.loc[count] = [l, '$\Delta t_1$', s.step]
        count += 1
        s = SumoSim(3000, 6000, links[l])
        op.loc[count] = [l, '$\Delta t_2$', s.step]
        count += 1
        s = SumoSim(6000, 9000, links[l])
        op.loc[count] = [l, '$\Delta t_3$', s.step]
        count += 1
    op.to_csv('travel_times.csv', index=False)
