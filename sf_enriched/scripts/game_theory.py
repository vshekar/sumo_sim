# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 16:42:33 2017

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
    SUMOBIN = 'sumo'
    SUMOCMD = [SUMOBIN, "-c", "../config/config_with_TLS.sumocfg", 
               "--time-to-teleport", "300",
               "--weight-files", "../config/link_weights.xml", 
               "--weight-attribute", "effort"]
    
    def __init__(self):
        self.network = sumolib.net.readNet('../network/SF_with_TLS.net.xml')
        self.edges = self.network.getEdges()
        self.edgeIDs = [edge.getID() for edge in self.edges]
        self.densities = defaultdict(float)
        self.delta = 28800
        self.gt = []
        self.epsilon = []
        self.curr_vuls = []
        self.prev_vuls = []
        self.weights = []
        self.t0_vuls = []
        self.corr = []
        self.pval = []
        self.total_epsilon = []
        self.total_vuls = []
        
        self.iteration = 1
        while self.stop_condition():
            try:
                
                self.prev_vuls = [x for x in self.curr_vuls]
                #Initialize and subscribe to data from the simulation 
                traci.start(self.SUMOCMD)
                #self.set_weights(0)
                #for edge in self.edges:
                for i in range(len(self.edgeIDs)):
                    traci.edge.subscribe(self.edgeIDs[i], 
                                         varIDs=(16,96), begin=0, end=86400000)
                self.run_sim()
                traci.close()
                self.generate_edge_weights()
                print('Iteration {}'.format(self.iteration))
                epsilon = ["%.3f" % v for v in self.epsilon]
                print(epsilon)
                vuls = ["%.3f" % v for v in self.curr_vuls]
                print(vuls)
                
                self.iteration += 1
            except KeyboardInterrupt or FatalTraCIError:
                print("Stopped algorithm at iteration {}".format(self.iteration))
                break 
    
    
     
    def generate_edge_weights(self):
        f = open('../config/link_weights.xml','w')
        op = "<meandata>\n"
        f.write(op)
        for i, g in enumerate(self.gt):
            op = '<interval begin="{}" end="{}" id="{}">\n'.format(i*self.delta, (i+1)*self.delta, i)
            f.write(op)
            #for edge in self.edges:
            for i in range(len(self.edgeIDs)):
                edge_id = self.edgeIDs[i]
                op = '<edge id="{}" effort="{}"/>\n'.format(edge_id, g.curr_tau[edge_id])
                f.write(op)
            op = '</interval>'
            f.write(op)
        op = "</meandata>"
        f.write(op)
        f.close()  
        
    def stop_condition(self):
        result = True
        if self.iteration > 1:
            ep = abs(sum(self.prev_vuls) - sum(self.curr_vuls))
            print('Epsilon = {}'.format(ep))
            self.total_epsilon.append(ep)
            self.total_vuls.append(sum(self.curr_vuls))
            if ep < 0.01:
                result = False
        
        return result
    
    def collect_interval_data(self, last_interval=False):
        if (self.step % self.delta == 0 or last_interval) and int(self.step/self.delta) > 0:
            if last_interval:
                interval = int(self.step/self.delta)
            else:
                interval = int(self.step/self.delta) - 1
            
            if interval >= len(self.gt):
                self.gt.append(GT(self.edges, interval))
                self.epsilon.append(float('Inf'))
                self.curr_vuls.append(0)
                self.prev_vuls.append(0)
                self.weights.append(0)
            
            print('Interval number = {}'.format(interval))             
            curr_gt = self.gt[interval]
            #for edge in self.edges:
            for i in range(len(self.edgeIDs)):
                #veh/unit length over interval
                self.densities[self.edgeIDs[i]] /= self.delta
            curr_gt.iterate(self.densities)
            self.densities = defaultdict(float)
            
    def collect_num_veh(self):
        #for edge in self.edges:
        for i in range(len(self.edgeIDs)):
            res = traci.edge.getSubscriptionResults(self.edgeIDs[i])
            if res != None:
                self.densities[self.edgeIDs[i]] += res[16]

    def calculate_all(self):
        self.collect_interval_data(last_interval=True)
        total_densities = 0
        total_tau_gamma = 0
        print('Length of gt = {}'.format(len(self.gt)))
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
            
            #self.weights[i] = gt.curr_tau
            self.epsilon[i] = abs(gt.curr_sys_vul - 
                        gt.prev_sys_vul)
            self.curr_vuls[i] = gt.curr_sys_vul
            
            gt.gamma.to_csv('gamma_v5_{}.csv'.format(i))
            gt.rho.to_csv('rho_v5_{}.csv'.format(i))
            gt.tau.to_csv('tau_v5_{}.csv'.format(i))
            gt.densities.to_csv('densities_v5_{}.csv'.format(i))
            gt.vulnerabilities.to_csv('vulnerability_v3_{}.csv'.format(i))
        
    def run_sim(self):
        self.arrived = 0
        self.step = 0
        
        while self.arrived < 50466:
            #self.set_weights()
            self.collect_interval_data()
            if self.iteration > 1:
                self.reroute_vehicles()
            traci.simulationStep()
            self.step += 1
            self.arrived += traci.simulation.getArrivedNumber()
            #Collects data for every second veh/unit length
            self.collect_num_veh()                          
        self.calculate_all()
    
    def reroute_vehicles(self):
        #for i in range(len(self.edgeIDs)):
        vehIDs = traci.simulation.getDepartedIDList()
        for vid in vehIDs:
            traci.vehicle.rerouteEffort(vid)
        
        
        
class GT():
    def __init__(self, edges, interval):
        self.edges = edges
        self.edgeIDs = [edge.getID() for edge in edges]
        self.interval = interval
        
        self.tau = pd.DataFrame()
        self.gamma = pd.DataFrame()
        self.rho = pd.DataFrame()
        self.densities = pd.DataFrame()
        self.vulnerabilities = pd.DataFrame()
        
        
        self.vulnerability = {}
        
        self.curr_rho = {}
        self.curr_gamma = {}
        self.curr_tau = defaultdict(float)
        self.curr_sys_vul = 0
        self.prev_sys_vul = 0
        
        self.iteration = 0
        
        self.beta = 1.0
        self.alpha = 1.0
        
        self.total_density = 0
        
        #for edge in self.edges:
        for i in range(len(self.edgeIDs)):
            edgeID = self.edgeIDs[i]
            self.curr_rho[edgeID] = 1/len(3*self.edges)
            self.curr_gamma[edgeID] = 0
            self.curr_tau[edgeID] = self.edges[i].getLength()/self.edges[i].getSpeed()
    
    def save_to_table(self):
        self.gamma = self.gamma.append(self.prev_gamma, ignore_index=True)
        self.rho = self.rho.append(self.prev_rho, ignore_index=True)
        self.tau = self.tau.append(self.prev_tau, ignore_index=True)
        self.densities = self.densities.append(self.avg_density, 
                                               ignore_index=True)
        #self.s_expected = self.s_expected.append(self.s_exp, ignore_index=True)
        self.vulnerabilities = self.vulnerabilities.append(self.vulnerability, 
                                                           ignore_index=True)
    
    
    def iterate(self, avg_density):
        self.avg_density = avg_density
        self.total_density = sum(self.avg_density.values())
        self.iteration += 1
        
        self.prev_rho = self.curr_rho
        self.prev_gamma = self.curr_gamma
        self.prev_tau = self.curr_tau
        self.curr_tau = defaultdict(float)
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
        for i in range(len(self.edgeIDs)):
            edgeID = self.edgeIDs[i]
            self.curr_tau[edgeID] = round((1/self.iteration**self.alpha)* self.s_exp[edgeID] +
                         (1 -(1/self.iteration**self.alpha)) * self.prev_tau[edgeID], 1)
                         
    def calc_gamma(self):
        for i in range(len(self.edgeIDs)):
            edgeID = self.edgeIDs[i]
            self.curr_gamma[edgeID] = (self.avg_density[edgeID]/
                               self.total_density)
    
    def calc_tau_gamma_prod(self):
        self.tau_gamma_prod = 0
        for i in range(len(self.edgeIDs)):
            edgeID = self.edgeIDs[i]
            self.tau_gamma_prod += (self.prev_tau[edgeID] * 
                                    self.curr_gamma[edgeID])
    
    def calc_rho(self):
        for i in range(len(self.edgeIDs)):
            edgeID = self.edgeIDs[i]
            self.curr_rho[edgeID] = ((self.prev_tau[edgeID] * 
                         self.curr_gamma[edgeID])/ self.tau_gamma_prod)
        
    def calc_sys_vul(self):
        sys_vul = 0
        for i in range(len(self.edgeIDs)):
            edgeID = self.edgeIDs[i]
            edge_vul = (self.curr_rho[edgeID] * self.curr_gamma[edgeID] *
                    self.curr_tau[edgeID])
            sys_vul += edge_vul
            self.vulnerability[edgeID] = edge_vul
        self.curr_sys_vul = sum(self.vulnerability.values())         
            
if __name__ == "__main__":
    s = SumoSim()
    f = open('alpha2_beta1-12_results.csv', 'w')
    for i in range(s.iteration - 1):
        f.write('{},{},{}\n'.format( i+1, s.total_epsilon[i], s.total_vuls[i]))
    f.close()