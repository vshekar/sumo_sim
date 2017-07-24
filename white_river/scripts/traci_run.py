import traci
import traci.constants as tc
import sumolib


class SumoSim():
    SUMOBIN = "sumo-gui"
    SUMOCMD = [SUMOBIN, "-c", "../config/config.sumocfg", "--ignore-route-errors", "true", "-W", "true", "--time-to-teleport", "-1"]

    
    def __init__(self):
        #Initialize simulation
        self.flood_files = ['../Flood intersections/flood1.txt', '../Flood intersections/flood2.txt', '../Flood intersections/flood3.txt', '../Flood intersections/flood4.txt', '../Flood intersections/flood5.txt', '../Flood intersections/flood6.txt']
        self.network = sumolib.net.readNet('../wr_selected.net.xml')
        traci.start(self.SUMOCMD)
        
            
        self.run_sim()
        
    def run_sim(self):
        self.step = 0
        file_count = 0
        while self.step < 3600:
            if self.step%1000 == 0:
                self.disable_links(file_count)
                file_count += 1
            #if self.step == 1000:
                #self.reenable_links()
            traci.simulationStep()
            self.step += 1
            
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
                        
    def reenable_links(self):
        for edge in self.disabled_edges:
            for lane in edge.getLanes():
                traci.lane.setAllowed(lane.getID(),[])

                
if __name__ == "__main__":
    s = SumoSim()