import traci
import traci.constants as tc
import sumolib
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict

#Potential 


class SumoSim():
    SUMOBIN = "sumo"
    SUMOCMD = [SUMOBIN, "-c", "../config/config.cfg", "--ignore-route-errors", "true", "-W", "true", "--time-to-teleport", "-1", 
                "--weight-files", "../config/link_weights.xml", "--weight-attribute", "traveltime"]

    def __init__(self, disc_edge=None, iteration=None, edges=None):
        self.disc_edge = disc_edge
        self.disc_iteration = iteration
        #Initialize simulation
        
        self.network = sumolib.net.readNet('../network/simple.net.xml')
        self.delta = 5
        #self.edges = [e for e in self.network.getEdges() if (e.getID() != '-1to0' and e.getID() != '5to-5')]
        if edges != None:
            self.edges = edges
        else:
            self.edges = [e for e in self.network.getEdges() if (e.getID() != '-1to0' and e.getID() != '5to-5')]
        
        #Create dataframes for T, gamma and rho
        self.T = pd.DataFrame()
        self.gamma_def = pd.DataFrame()
        self.rho_att = pd.DataFrame()
        
        #Densities for links and network (Can be changed to other metrics)
        self.densities = defaultdict(float)
        self.total_density = 0
        
        #Initialize and subscribe to data from the simulation 
        traci.start(self.SUMOCMD)
        for edge in self.edges:
            traci.edge.subscribe(edge.getID(), varIDs=(16,96), begin=0, end=86400000)
        self.allVehiclesReroute = True
        self.init_gt()

        self.run_sim()
        #print(self.rho_att)
        #self.rho_att.to_csv('rho.csv')
        #self.gamma_def.to_csv('gamma.csv')
        #self.T.to_csv('T.csv')
    
    def init_gt(self):
        t = {}
        g = {}
        r = {}
        for edge in self.edges:
            el = edge.getLength()
            sp = edge.getSpeed()
            t[edge.getID()] = el/sp

            g[edge.getID()] = 0

            r[edge.getID()] = 1/len(self.edges)

        self.T = self.T.append(t, ignore_index=True)
        self.gamma_def = self.gamma_def.append(g, ignore_index=True)
        self.rho_att = self.rho_att.append(r, ignore_index=True)

    def run_sim(self):
        self.arrived = 0
        self.step = 0
        self.iteration = 1
        while self.arrived < 500:
            vehIDs = traci.edge.getLastStepVehicleIDs('-1to0')
            for id in vehIDs:
                traci.vehicle.rerouteTraveltime(id, currentTravelTimes=False)
            traci.simulationStep()
            self.step += 1
            self.arrived += traci.simulation.getArrivedNumber()
            self.calc_density()
            
            #Actually disconnecting link!
            #disc_edge = '5to3'
            if self.iteration == self.disc_iteration and self.disc_edge != None:
                print("Disconnecting")
                for edge in self.edges:
                    if edge.getID() == self.disc_edge:
                        for lane in edge.getLanes():
                            traci.lane.setDisallowed(lane.getID(),['passenger'])
            elif self.iteration == self.disc_iteration+1 and self.disc_edge != None:
                print("Reconnecting!")
                for edge in self.edges:
                    if edge.getID() == self.disc_edge:
                        for lane in edge.getLanes():
                            traci.lane.setAllowed(lane.getID(),[])
            
            
            
            if self.step % self.delta == 0:
                self.gt_calc()
                if self.allVehiclesReroute:
                    for edge in self.edges:
                        vehIDs = traci.edge.getLastStepVehicleIDs(edge.getID())
                        for id in vehIDs:
                            traci.vehicle.rerouteTraveltime(id, currentTravelTimes=False)
                self.iteration += 1 
    
        traci.close()            
        
    def gt_calc(self):
        print("GT Calc")
        t = {}
        g = {}
        r = {}
        prev_t = self.T.iloc[-1]
        rho_denom = 0
        for edge in self.edges:
            #******** ROUTER STRATEGY *******************
            #Get rho of previous iteration
            prev_rho = self.rho_att.iloc[-1][edge.getID()]
            
            #S-expected cost calculation
            fft = edge.getLength()/edge.getSpeed()
            s = ((1 - prev_rho) * fft) + (prev_rho * len(self.edges) * fft)
            
            #MSA of s-expected cost
            t[edge.getID()] = (1/self.iteration) * s + (1-1/self.iteration) * self.T.iloc[-1][edge.getID()] 
            self.increase_len(edge.getID(), t[edge.getID()])
            
            #************ TESTER STRATEGY ******************
            #Gamma calculation 
            g[edge.getID()] = self.densities[edge.getID()]/self.delta
            rho_denom += g[edge.getID()] * prev_t[edge.getID()]
        
        for edge in self.edges:
            #Calculate Link Failure Probability, rho
            r[edge.getID()] = (g[edge.getID()] * prev_t[edge.getID()]) / rho_denom           
        self.densities = defaultdict(float)
        self.T = self.T.append(t, ignore_index=True)
        self.gamma_def = self.gamma_def.append(g, ignore_index=True)
        self.rho_att = self.rho_att.append(r, ignore_index=True)   
       
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
