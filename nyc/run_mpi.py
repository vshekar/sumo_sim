from mpi4py import MPI
import subprocess
import glob

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
#f = open('rank'+str(rank),'w')
#f.writelines('My rank is : ' + str(rank))
#f.close()

def start():
    configs = glob.glob('/people/shek628/sim/nyc/config/config*')
    counter = 0
    for config in configs:
        if rank == counter:
            log = open("log"+str(rank),'w')
            suffix = '_' + edge[0] + '__' +str(interval[0]) + '_' +str(interval[1])
            #generate_config(edge,interval,suffix)
            #generate_additional(edge,G,interval,intervals,suffix)
            #print suffix +'\n'
            sumoProcess = subprocess.Popen(['sumo',"--time-to-teleport","-1", "-c", config], stdout=log, stderr=log)
            sumoProcess.wait()
            log.flush()
            log.close()
        counter += 1

    print rank

start()
