from __future__ import absolute_import
from __future__ import print_function
import subprocess
import os, sys
import traci
import traci.constants as tc

sumoBinary = "C:/Program Files (x86)/DLR/Sumo/bin/sumo.exe"

sumoCmd = [sumoBinary, "-c", "../config/config.sumocfg"]
sumoConfig = "../config/config.sumocfg"

#sumoProcess = subprocess.Popen([sumoBinary, sumoConfig], stdout=sys.stdout, stderr=sys.stderr)
traci.start(sumoCmd)
#traci.init(8000)
#traci.simulation.subscribe()
vehID = "0"
traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))
step = 0

while step < 1000:
	#print("step {}".format(step))
	traci.simulationStep()
	print(traci.vehicle.getSubscriptionResults(vehID))
	step += 1

traci.close()