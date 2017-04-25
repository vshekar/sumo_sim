from mpi4py import MPI
import subprocess
import glob
from traci_sim import SumoSim
from shutil import copyfile

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
#f = open('rank'+str(rank),'w')
#f.writelines('My rank is : ' + str(rank))
#f.close()

def start():
    copyfile('test.db','proc{}.db'.format(rank))
    for i in range(1825):
        if rank == int(i/25):
            ss = SumoSim(rank)
            sims = ss.get_sim()
            #log = open("log"+str(rank),'w')
            ss.run_sim(sims[i])
            #log.flush()
            #log.close()
        #counter += 1

            print rank

start()
