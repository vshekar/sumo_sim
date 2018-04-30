import sumolib
import pandas as pd
import numpy as np
import traci
import xml.etree.ElementTree as ET
from subprocess import call
import pickle
    

class Simulation():
    def __init__(self, network, total_trips, interval_time, tripfile = None, vul_link = None):
        self.network = network
        self.total_trips = total_trips
        self.interval_time = interval_time
        self.tripfile = tripfile
        self.vul_link = vul_link
        self.SUMOBIN = 'sumo'
        self.SUMOCMD = [self.SUMOBIN, "-c", "../config/config.sumocfg", 
               "--time-to-teleport", "300", "--vehroutes", "../output/vehroutes.xml",
                        "--vehroute-output.route-length", "true"]
        self.edges = network.getEdges()
        self.edgeIDs = [edge.getID() for edge in self.edges]




    def parse_routes(self, routefile):
        tree = ET.parse(routefile)
        root = tree.getroot()
        for vehicle in root:
            vehID = vehicle.attrib['id']
            time = float(vehicle.attrib['arrival']) - float(vehicle.attrib['depart'])
            dist = float(vehicle.attrib['routeLength'])
            self.result.loc[int(vehID), 'v_cost'] = dist
            self.result.loc[int(vehID), 't_cost'] = time

    def generate_additional(self, edge, interval, rerouters, default=False):
        additional_filepath = '../config/additional.xml'
        f = open(additional_filepath, 'w')
        if default:
            lines = ("<additional>\n"
                     "    <vType id=\"passenger\">\n"
                     "        <param key=\"has.rerouting.device\" value=\"true\"/>\n"
                     "    </vType>\n"
                     "</additional>")
        else:
            lines = ('<additional>\n'
                     '<rerouter id="1" edges="' + rerouters + '">\n'
                         '<interval begin="' + str(interval[0]) + '" end="' + str(
                            interval[1]) + '">\n'
                         '<closingReroute id="' + edge.getID() + '"/>\n'
                     '</interval>\n'
                     '</rerouter>\n'
                     '</additional>\n')
        f.write(lines)

    def simulate_traci(self):
        traci.start(self.SUMOCMD)
        for i in range(len(self.edgeIDs)):
            traci.edge.subscribe(self.edgeIDs[i],
                                 varIDs=(16, 96), begin=0, end=86400000)
        self.arrived = 0
        self.step = 0
        if self.vul_link is None:
            while self.arrived < self.total_trips:
                #try:
                    traci.simulationStep()
                    self.step += 1
                    self.arrived += traci.simulation.getArrivedNumber()
                    self.arrived_list = traci.simulation.getStopEndingVehiclesIDList()
                    for vehID in self.arrived_list:
                        self.result.loc[int(vehID), 'v_cost'] = \
                            traci.vehicle.getDistance(vehID)

                        self.result.loc[int(vehID), 't_cost'] = \
                            self.step - \
                            self.result.loc[int(vehID), 't_cost']


    def simulate(self):
        call(self.SUMOCMD)
        self.parse_routes('../output/vehroutes.xml')

    def reset_data(self):
        trips = np.asarray([str(i) for i in range(total_trips)])
        v_cost = np.zeros_like(trips)
        t_cost = np.zeros_like(trips)
        d = {'trip_id': trips, 'v_cost': v_cost, 't_cost': t_cost,
             'source': self.source, 'dest': self.dest}
        self.result = pd.DataFrame(data=d)
        self.result.set_index('trip_id')

    def parse_trips(self, tripfile):
        tree = ET.parse(tripfile)
        root = tree.getroot()
        self.source = []
        self.dest = []
        for trip in root:
            self.source.append(trip.attrib['from'])
            self.dest.append(trip.attrib['to'])

    def run_all(self):
        self.result_list = {}
        self.parse_trips(self.tripfile)
        self.reset_data()
        self.generate_additional(0,0,0,default=True)
        self.simulate()
        self.result_list['nominal'] = self.result

        for edge in self.edges:
            rerouters = [e.getID() for e in edge.getIncoming()]
            rerouters = " ".join(rerouters)
            for interval in range(0, 5000, 1000):
                self.reset_data()
                self.generate_additional(edge, [interval, interval+1000], rerouters)
                self.simulate()
                label = "{} {} {}".format(edge.getID(), interval, interval + 1000)
                self.result_list[label] = self.result


if __name__ == "__main__":
    network = sumolib.net.readNet('../network/grid.net.xml')
    total_trips = 3600
    interval_time = 1000
    s = Simulation(network, total_trips, interval_time, tripfile='../trips/trips.xml')
    s.run_all()
    f = open('../output/result_list', 'wb')
    pickle.dump(s.result_list, f)
    f.close()

