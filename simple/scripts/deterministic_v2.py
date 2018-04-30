import sumolib
import pandas as pd
import numpy as np
import traci
import xml.etree.ElementTree as ET
from subprocess import call
import pickle




class Simulation():
    def __init__(self, network, total_trips, interval_time, tripfile=None, vul_link=None):
        self.network = network
        self.total_trips = total_trips
        self.interval_time = interval_time
        self.vul_link = vul_link
        self.SUMOBIN = 'sumo-gui'
        self.SUMOCMD = [self.SUMOBIN, "-c", "../config/config.sumocfg",
                        "--time-to-teleport", "300", "--vehroutes", "../output/vehroutes.xml",
                        "--vehroute-output.route-length", "true"]
        self.SUMOMESO = [self.SUMOBIN, "-c", "../config/config.sumocfg",
                        "--time-to-teleport", "300", "--vehroutes", "../output/vehroutes.xml",
                        "--vehroute-output.route-length", "true", "--mesosim", "t"]
        self.edges = network.getEdges()
        self.edgeIDs = [edge.getID() for edge in self.edges]

    def parse_routes(self, routefile):
        tree = ET.parse(routefile)
        root = tree.getroot()
        for vehicle in root:
            vehID = vehicle.attrib['id']
            time = float(vehicle.attrib['arrival']) - float(vehicle.attrib['depart'])
            dist = float(vehicle.attrib['routeLength'])
            depart = float(vehicle.attrib['depart'])
            self.result.loc[int(vehID), 'v_cost'] = dist
            self.result.loc[int(vehID), 't_cost'] = time
            self.result.loc[int(vehID), 'depart'] = depart

    def generate_additional(self, edge, interval, rerouters, default=False):
        additional_filepath = '../config/additional.xml'
        f = open(additional_filepath, 'w')
        if default:
            lines = ("<additional>\n"
                     "    <vType id=\"passenger\">\n"
                     "        <param key=\"has.rerouting.device\" value=\"true\"/>\n"
                     "    </vType>\n"
                     "</additional>")
        elif rerouters == '':
            lines = ('<additional>\n'
                     '<interval begin="' + str(interval[0]) + '" end="' + str(
                interval[1]) + '">\n'
                               '<closingReroute id="' + edge.getID() + '"/>\n'
                                                                       '</interval>\n'
                                                                       '</additional>\n')

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
                # try:
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
        call(self.SUMOMESO)
        self.parse_routes('../output/vehroutes.xml')

    def reset_data(self):
        trips = np.asarray([str(i) for i in range(500)])
        v_cost = np.zeros_like(trips)
        t_cost = np.zeros_like(trips)
        depart = np.zeros_like(trips)
        d = {'trip_id': trips, 'v_cost': v_cost, 't_cost': t_cost, 'depart': depart}
        self.result = pd.DataFrame(data=d)
        self.result.set_index('trip_id')

    def get_mean_TT(self, attrib):
        tree = ET.parse('../output/summary.xml')
        root = tree.getroot()
        return float(root[-1].attrib[attrib])


    def run_all(self):
        self.result_list = {}
        self.mean_TT = {}
        self.sim_time = {}
        self.reset_data()
        self.generate_additional(0, 0, 0, default=True)
        self.simulate()
        self.result_list['nominal'] = self.result
        self.mean_TT['nominal'] = self.get_mean_TT('meanTravelTime')
        self.sim_time['nominal'] = self.get_mean_TT('time')


        for edge in self.edges:
            if edge.getID() != '-1to0' and edge.getID() != '5to-5':
                rerouters = [e.getID() for e in edge.getIncoming()]
                rerouters = " ".join(rerouters)
                for interval in range(0, 1500, 500):
                    self.reset_data()
                    self.generate_additional(edge, [interval, interval + 500], rerouters)
                    self.simulate()
                    label = "{} {} {}".format(edge.getID(), interval, interval+500)
                    self.result_list[label] = self.result
                    self.mean_TT[label] = self.get_mean_TT('meanTravelTime')
                    self.sim_time[label] = self.get_mean_TT('time')






if __name__ == "__main__":
    network = sumolib.net.readNet('../network/simple.net.xml')
    total_trips = 500
    interval_time = 1000
    s = Simulation(network, total_trips, interval_time, tripfile='../trips/trip.xml')

    result = s.run_all()
    vul = {}
    s.result_list['nominal']['prod'] = s.result_list['nominal']['t_cost'] * \
                                       s.result_list['nominal']['v_cost']

    for sim in s.result_list.keys():
        if sim != 'nominal':
            vul[sim] = sum(
            (s.result_list[sim]['t_cost'] * s.result_list[sim]['v_cost'] -
            s.result_list['nominal']['prod']) / (s.result_list['nominal']['prod']))

    f = open('sim_result_meso', 'wb')
    pickle.dump(s.result_list, f)
    f.close()
"""
app = dash.Dash()
app.layout = html.Div(children=[
    html.H1(children='Vulnerability Assessment'),
    dcc.Graph(
        id='travel-time-graph',
        figure={
            'data': [
                    {'x': s.result_list['nominal']['depart'],
                     'y': s.result_list['nominal']['t_cost'],
                     'type': 'bar',
                     'name': 'Nominal'
                     },
                    {
                    'x': s.result_list['0to2 0 500']['depart'],
                    'y': s.result_list['0to2 0 500']['t_cost'],
                    'type': 'bar',
                    'name': '0to2 0 500'
                    }
                    ],
            'layout': {
                'title':'Travel time Viz'
            }
        }
    )
])
app.run_server(debug=True)"""



