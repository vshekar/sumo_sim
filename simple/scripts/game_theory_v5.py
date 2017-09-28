# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 15:49:11 2017

@author: Shekar
"""

import pandas as pd
import traci
import sumolib
from collections import defaultdict
import scipy.stats

class SumoSim():
    SUMOBIN = "sumo"
    SUMOCMD = [SUMOBIN, "-c", "../config/config.cfg", "--time-to-teleport", "-1",
               "--weight-files", "../config/link_weights.xml", 
               "--weight-attribute", "effort"]
    
    def __init__(self):
        self.network = sumolib.net.readNet('../network/simple.net.xml')
        self.edges = [e for e in self.network.getEdges() if 
                      (e.getID() != '-1to0' and e.getID() != '5to-5')]
        self.densities = defaultdict(float)
        self.delta = 500
        self.gt = [GT(self.edges, 0), GT(self.edges, 1), GT(self.edges, 2)]
        self.epsilon = [float('Inf'), float('Inf'), float('Inf')]
        self.curr_vuls = [0.0,0.0,0.0]
        self.weights = [0,0,0]
        
        self.iteration = 1
        while self.stop_condition():
            #Initialize and subscribe to data from the simulation 
            print('Iteration {}'.format(self.iteration))
            traci.start(self.SUMOCMD)
            #self.set_weights(0)
            for edge in self.edges:
                traci.edge.subscribe(edge.getID(), 
                                     varIDs=(16,96), begin=0, end=86400000)
            self.run_sim()
            traci.close()
            self.generate_edge_weights()
            epsilon = ["%.3f" % v for v in self.epsilon]
            print(epsilon)
            vuls = ["%.3f" % v for v in self.curr_vuls]
            print(vuls)
            self.iteration += 1
    
    def generate_edge_weights(self):
        op = "<meandata>\n"
        for i, g in enumerate(self.gt):
            op += '<interval begin="{}" end="{}" id="{}">\n'.format(i*self.delta, (i+1)*self.delta, i)
            for edge in self.edges:
                edge_id = edge.getID()
                #if edge_id == '0to2':
                #    op += '<edge id="{}" effort="{}"/>\n'.format(edge_id, 10000000.0)
                #else:
                op += '<edge id="{}" effort="{}"/>\n'.format(edge_id, g.curr_tau[edge_id])
            op+= '</interval>'
        
        op += "</meandata>"
        f = open('../config/link_weights.xml','w')
        f.write(op)
        f.close()
        
    
    def stop_condition(self):
        result = True
        if (abs(self.epsilon[0]) <= 0.01 and 
              abs(self.epsilon[1]) <= 0.01 and abs(self.epsilon[2]) <= 0.01):
            result = False
        
        return result
    
    def set_weights(self):
        interval = int(self.step/self.delta)
        if self.step % self.delta == 0 and self.iteration > 1 and interval < 3:
            curr_gt = self.gt[interval]
            for edge in self.edges:
                edgeID = edge.getID()
                traci.edge.setEffort(edgeID, curr_gt.curr_tau[edgeID])
                traci.edge.adaptTraveltime(edgeID, curr_gt.curr_tau[edgeID])
                
        
    
    def collect_interval_data(self):
        if self.step % self.delta == 0 and int(self.step/self.delta) > 0:
            interval = int(self.step/self.delta) - 1
            curr_gt = self.gt[interval]
            for edge in self.edges:
                #veh/unit length over interval
                self.densities[edge.getID()] /= self.delta
            curr_gt.iterate(self.densities)
            self.densities = defaultdict(float)
    
    def reroute_vehicles(self):
        if self.iteration > 1:
            vehIDs = traci.edge.getLastStepVehicleIDs('-1to0')
            for vid in vehIDs:
                #for edge in self.edges:
                #    e_effort = 0
                    #e_effort = traci.edge.getAdaptedTraveltime(edge.getID(), self.step)
                    
                    #traci.vehicle.setAdaptedTraveltime(vid, 0, 2000, edge.getID(), e_effort)
                    #traci.vehicle.setEffort(vid, 0, 2000, edge.getID(), e_effort)
                
                #e_tt = traci.edge.getEffort('0to1', self.step)
                #traci.vehicle.setEffort(vid, 0, 2000, '0to1', e_tt)
                #v_tt = traci.vehicle.getEffort(vid, self.step, '0to1')
                #v_effort = traci.vehicle.getAdaptedTraveltime(vid, self.step, '0to1')
                #e_effort = traci.edge.getAdaptedTraveltime('0to1', self.step)
                
                #if v_tt != e_tt:
                #print("not equal! {} {}".format(v_tt, e_tt))
                traci.vehicle.rerouteEffort(vid)
                #traci.vehicle.rerouteTraveltime(vid, currentTravelTimes=True)
   
    def collect_num_veh(self):
        for edge in self.edges:
            res = traci.edge.getSubscriptionResults(edge.getID())
            if res != None:
                self.densities[edge.getID()] += res[16]
    
    def calculate_all(self):
        total_densities = 0
        total_tau_gamma = 0
        for gt in self.gt:
            total_densities += gt.total_density
        
        for gt in self.gt:
            gt.total_density = total_densities
            gt.calc_gamma()
            gt.calc_tau_gamma_prod()
            total_tau_gamma += gt.tau_gamma_prod
        for i,gt in enumerate(self.gt):
            gt.tau_gamma_prod = total_tau_gamma
            gt.calc_rho()
            
            gt.calc_s_expected()
            gt.calc_edge_cost()
            gt.calc_sys_vul()
            
            self.weights[i] = gt.curr_tau
            self.epsilon[i] = abs(gt.curr_sys_vul - 
                        gt.prev_sys_vul)
            self.curr_vuls[i] = gt.curr_sys_vul
            
            gt.gamma.to_csv('gamma_v3_{}.csv'.format(i))
            gt.rho.to_csv('rho_v3_{}.csv'.format(i))
            gt.tau.to_csv('tau_v3_{}.csv'.format(i))
            gt.densities.to_csv('densities_v3_{}.csv'.format(i))
            gt.vulnerabilities.to_csv('vulnerability_v3_{}.csv'.format(i))
    
    
    def run_sim(self):
        self.arrived = 0
        self.step = 0
        
        while self.arrived < 500:
            #self.set_weights()
            self.collect_interval_data()
            self.reroute_vehicles()
            traci.simulationStep()
            self.step += 1
            self.arrived += traci.simulation.getArrivedNumber()
            #Collects data for every second veh/unit length
            self.collect_num_veh()                          
        self.calculate_all()   
            
class GT():
    def __init__(self, edges, interval):
        self.edges = edges
        self.interval = interval
        
        self.tau = pd.DataFrame()
        self.gamma = pd.DataFrame()
        self.rho = pd.DataFrame()
        self.densities = pd.DataFrame()
        self.vulnerabilities = pd.DataFrame()
        
        self.vulnerability = {}
        
        self.curr_rho = {}
        self.curr_gamma = {}
        self.curr_tau = {}
        self.curr_sys_vul = 0
        self.prev_sys_vul = 0
        
        self.iteration = 0
        
        self.beta = 1.0/12.0
        self.alpha = 2.0
        
        for edge in self.edges:
            edgeID = edge.getID()
            self.curr_rho[edgeID] = 1/len(3*self.edges)
            self.curr_gamma[edgeID] = 0
            self.curr_tau[edgeID] = edge.getLength()/edge.getSpeed()
    
    def save_to_table(self):
        self.gamma = self.gamma.append(self.prev_gamma, ignore_index=True)
        self.rho = self.rho.append(self.prev_rho, ignore_index=True)
        self.tau = self.tau.append(self.prev_tau, ignore_index=True)
        self.densities = self.densities.append(self.avg_density, 
                                               ignore_index=True)
        self.vulnerabilities = self.vulnerabilities.append(self.vulnerability, 
                                                           ignore_index=True)
    
    
    def iterate(self, avg_density):
        self.avg_density = avg_density
        self.total_density = sum(self.avg_density.values())
        self.iteration += 1
        
        self.prev_rho = self.curr_rho
        self.prev_gamma = self.curr_gamma
        self.prev_tau = self.curr_tau
        self.prev_sys_vul = self.curr_sys_vul
        
        self.save_to_table()
        
    def calc_s_expected(self):
        self.s_exp = {}
        for edge in self.edges:
            edgeID = edge.getID()
            fft = edge.getLength()/edge.getSpeed()
            self.s_exp[edgeID] = ((1 - self.curr_rho[edgeID]) * fft + 
                      self.beta * self.curr_rho[edgeID] * len(self.edges) 
                      * fft)
            
    def calc_edge_cost(self):
        for edge in self.edges:
            edgeID = edge.getID()
            self.curr_tau[edgeID] = ((self.alpha/self.iteration)* self.s_exp[edgeID] +
                         (1 -(self.alpha/self.iteration)) * self.prev_tau[edgeID])
                         
    def calc_gamma(self):
        for edge in self.edges:
            edgeID = edge.getID()
            self.curr_gamma[edgeID] = (self.avg_density[edgeID]/
                               self.total_density)
    
    def calc_tau_gamma_prod(self):
        self.tau_gamma_prod = 0
        for edge in self.edges:
            edgeID = edge.getID()
            self.tau_gamma_prod += (self.prev_tau[edgeID] * 
                                    self.curr_gamma[edgeID])
    
    def calc_rho(self):
        for edge in self.edges:
            edgeID = edge.getID()
            self.curr_rho[edgeID] = ((self.prev_tau[edgeID] * 
                         self.curr_gamma[edgeID])/ self.tau_gamma_prod)
        
    def calc_sys_vul(self):
        sys_vul = 0
        for edge in self.edges:
            edgeID = edge.getID()
            edge_vul = (self.curr_rho[edgeID] * self.curr_gamma[edgeID] *
                    self.prev_tau[edgeID])
            sys_vul += edge_vul
            self.vulnerability[edgeID] = edge_vul
        self.curr_sys_vul = sum(self.vulnerability.values())  


if __name__ == "__main__":
    s = SumoSim()
    travel_times = [1665,1672,1638,1638,1672,1638,1702,1638,1645,1638,1638,
                    1668,1638,1658,1664,1638,1638,1667,1638,1738,1638,1659,
                    1638,1638,1681,1638,1669,1668,1638,1638,1769,1638,1817,
                    1638,1735,1638,1638,1735,1638]
    vul_list = []
    for g in s.gt:
        vul_list += g.vulnerabilities.values.tolist()[-1]
    print(vul_list)
    print(scipy.stats.spearmanr(travel_times, vul_list))
    
    d = dict(zip(travel_times, vul_list))
    print(sorted(d.values()))
    
    
    short_vul = []
    short_travel = []
    for i, vul in enumerate(vul_list):
        if vul != 0:
            short_vul.append(vul)
            short_travel.append(travel_times[i])
    print("")
    print(short_travel)
    print(short_vul)
    print(scipy.stats.spearmanr(short_travel, short_vul))
           