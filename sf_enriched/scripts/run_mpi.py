from mpi4py import MPI
import subprocess
import glob
from traci_sim import SumoSim

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
#f = open('rank'+str(rank),'w')
#f.writelines('My rank is : ' + str(rank))
#f.close()

def start():
    ss = SumoSim()
    sims = ss.get_sim()
    for i in range(len(sims)):
        if rank == i:
            log = open("log"+str(rank),'w')
            ss.run_sim(sims[i])
            log.flush()
            log.close()
        counter += 1

    print rank

start()