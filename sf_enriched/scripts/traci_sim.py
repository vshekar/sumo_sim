import sys,os,traci
from inspect import signature,getmembers

sumoBinary = "sumo"

sumoCmd = [sumoBinary, "-c", "../config/config_with_TLS.sumocfg"]
traci.start(sumoCmd)
step = 0

while step < 10:
	traci.simulationStep()
	if step == 1:
		print("Adding person")
		p = traci._person.PersonDomain()
		print(getmembers(p))
		for member in getmembers(p):
			print(member)
		#p.add("P1", "10_1", 0.0, depart=-3, typeID='DEFAULT_PEDTYPE')
		#p.appendDrivingStage("P1", "38_1")
		#print(signature(p.appendDrivingStage))
	step += 1

traci.close()