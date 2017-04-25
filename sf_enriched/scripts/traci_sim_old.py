"""
This module runs a traci simulation and connects to the local sqlite3 db to store results
"""
from __future__ import print_function
from sqlalchemy import create_engine, null
from sqlalchemy.orm import sessionmaker
from setup_database import SimData, SimStats, SubLinks, LinkStats, Base, Links
from collections import defaultdict
from multiprocessing import Pool
import traci
import sumolib
import xml.etree.ElementTree as ET
from collections import deque
from shutil import copyfile

class SumoSim():
    """
    tree = ET.parse('../trips/trip.xml')
    trips = tree.getroot()
    all_trips = []
    for t in trips:
        all_trips.append((t.attrib['id'],t.attrib['depart'],t.attrib['from'],t.attrib['to']))
    all_trips = deque(all_trips)
    """


    SUMOBIN = "sumo"

    SUMOCMD = [SUMOBIN, "-c", "../config/config_with_TLS.sumocfg", "--ignore-route-errors", "true", "-W", "true", "--time-to-teleport", "300"]
       #print(all_sublinks)
    def __init__(self, rank):
        self.rank = rank
        #copyfile('test.db','proc{}.db'.format(rank))
        ENGINE = create_engine('sqlite:///proc{}.db'.format(rank), connect_args={'timeout':15})
        Base.metadata.bind = ENGINE
        self.DBSession = sessionmaker(bind=ENGINE)
        self.SESSION = self.DBSession()
        self.all_sublinks = self.SESSION.query(SubLinks, Links).filter(SubLinks.link == Links.link_id).all()



    def run_sim(self, sim):
        """Runs simulation"""
        traci.start(self.SUMOCMD)
        
        #conn = traci.connect(port)
        for sublink, link in self.all_sublinks:
            edgeID = str(link.link) + "_" + str(sublink.sublink)
            traci.edge.subscribe(edgeID, varIDs=(96,100,101,16), begin=0, end=86400000)
        step = 0
        start_disruption = sim.start_time
        end_disruption = sim.end_time
        sim_id = sim.sim_id
        link_disrupted = sim.link
        if link_disrupted != None:
            disrupted_sublinks = self.SESSION.query(SubLinks).filter(SubLinks.link == Links.link_id).filter(Links.link == link_disrupted).all()
            sl = []
            for subl in disrupted_sublinks:
                sl.append(str(link_disrupted)+ "_" + str(subl.sublink))
            


        #Amount of time to wait for aggregation
        delta = 3600
        begin_delta = 0
        end_delta = begin_delta + delta

        avg_density = defaultdict(float)
        cumu_CO2 = defaultdict(float)
        cumu_NOx = defaultdict(float)
        cumu_fuel = defaultdict(float)
        vehicle_number = 0
        stopped_vehicles = []
        while step < 86400:
            traci.simulationStep()
            step += 1

            #Add vehicle code
            """
            vehicles = self.get_vehicles(step)
            for vehicle in vehicles:
                if start_disruption <= step <= end_disruption and vehicle[2].split('_')[0] == str(link_disrupted):
                    stopped_vehicles.append((str(vehicle_number), vehicle[2], vehicle[3]))
                else:
                    try:
                        traci.route.add(str(vehicle_number), [vehicle[2], vehicle[3]])
                        traci.vehicle.add(str(vehicle_number),str(vehicle_number), typeID="reroutingType")
                    except:
                        print(vehicle[2].split('_')[0], vehicle[3].split('_')[0], str(link_disrupted))
                        pass
                vehicle_number +=1
	    """

            #Disruption code
            if start_disruption == step:
                for sl in disrupted_sublinks:
                    for i in range(sl.num_lanes):
                        traci.lane.setDisallowed(str(link_disrupted)+ "_" + str(sl.sublink) + "_" + str(i),['passenger'])
                print("Add disruption here!")
            elif end_disruption == step:
                print("Remove disruption here!")
                for sl in disrupted_sublinks:
                    for i in range(sl.num_lanes):
                        traci.lane.setAllowed(str(link_disrupted)+ "_" + str(sl.sublink) + "_" + str(i),[])

            """		
	    if step > end_disruption and len(stopped_vehicles) > 0:
		#for vehicle in stopped_vehicles:
		vehicle = stopped_vehicles.pop()
		try:
                    traci.route.add(str(vehicle[0]), [vehicle[1], vehicle[2]])
                    traci.vehicle.add(str(vehicle[0]),str(vehicle[0]), typeID="reroutingType")
                except:
                    print("Stopped vehicle cannot be added")
                    pass
	        #stopped_vehicles = [] 
            """
	    #elif step > end_disruption:
                          
            #Data collection code
            if begin_delta < step <= end_delta:
                for sublink, link in self.all_sublinks:
                    sublink_id = sublink.sublink_id
                    link_name = str(link.link) + "_" + str(sublink.sublink)
                    res = traci.edge.getSubscriptionResults(link_name)
                    if res != None:
                        cumu_CO2[sublink_id] += res[96]
                        cumu_NOx[sublink_id] += res[100]
                        avg_density[sublink_id] += res[16]
                        cumu_fuel[sublink_id] += res[101]
                if step == end_delta:
                    self.save_link_stats(sim_id, cumu_CO2, cumu_NOx, cumu_fuel, avg_density, begin_delta, end_delta)
                    begin_delta += delta
                    end_delta += delta
                    avg_density = defaultdict(float)
                    cumu_CO2 = defaultdict(float)
                    cumu_NOx = defaultdict(float)
        	    cumu_fuel = defaultdict(float)

        vehicle_number = 0
            
        traci.close()

    def get_vehicles(self, step):
        vehicles = []
        while(len(self.all_trips)>0 and int(self.all_trips[0][1])<=step):
            vehicles.append(self.all_trips.popleft())
        return vehicles



    def save_link_stats(self, sim_id, cumu_CO2, cumu_NOx, cumu_fuel, avg_density, start_time, end_time):
        for sublink,link in self.all_sublinks:
            sublink_id = sublink.sublink_id
            avg_density[sublink_id] = avg_density[sublink_id]/(end_time-start_time)
            
            l = LinkStats(sim_num=sim_id, sublink=sublink_id, density=avg_density[sublink_id], \
            CO2=cumu_CO2[sublink_id], NO2=cumu_NOx[sublink_id], fuel=cumu_fuel[sublink_id], start_time=start_time, end_time=end_time)
            self.SESSION.add(l)
            #print(link_name)
        self.SESSION.commit()


    def get_sim(self):
        """Get correct simulation"""
        sim = self.SESSION.query(SimData).all()
        return sim

    def setup_sim(self, start_sim, end_sim):
        """Setup network for simulation"""
        sims = self.get_sim()
        """
        for i,sim in enumerate(sims):
            print("Running simulation {} of {}".format(i+1, len(sims)))
            run_sim(sim)
        """
        #p = Pool(1)
        #p.map(self.run_sim, sims)
        print(len(sims))
        for sim in sims[start_sim:end_sim]:
            self.run_sim(sim)


#if __name__ == "__main__":
    #ss = SumoSim(0)
    #ss.setup_sim(0,3)
    
