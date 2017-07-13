from mpi4py import MPI
from game_theory import SumoSim
import pandas as pd
import sumolib

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def start():
    network = sumolib.net.readNet('../network/simple.net.xml')
    edges = [e for e in network.getEdges() if (e.getID() != '-1to0' and e.getID() != '5to-5')]
    sim_time = pd.DataFrame()
    for i in range(345):
        #if rank == i:
            t = {}
            t['interval'] = i
            for edge in edges:
                s = SumoSim(edge.getID(), i, edges)
                t[edge.getID()] =  s.step
		
            sim_time = sim_time.append(t, ignore_index=True)
    sim_time.to_csv('second_sim_' + str(rank) + '.csv')


start()
