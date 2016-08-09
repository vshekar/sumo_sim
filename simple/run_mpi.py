from mpi4py import MPI
import subprocess

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
#f = open('rank'+str(rank),'w')
#f.writelines('My rank is : ' + str(rank))
#f.close()

def start():
    suffix = ""
    vul_edges = ['4to5','3to5','3to4','1to3','2to4','1to2','0to1','0to2']
    dest_edges = ['4to5','3to5']
    intervals = [(0,500),(500,1000),(1000,1500)]
    counter = 0
    for edge in vul_edges:
        for interval in intervals:
            if rank == counter:
                print str(counter) + " <- Rank"
                
                log = open("log"+str(rank), 'w')
	        suffix = '_' + edge + '__' +str(interval[0]) + '_' +str(interval[1])
	        #generate_config(edge,interval,suffix)
	        #generate_additional(edge,G,interval,intervals,suffix)
	        print suffix +'\n'
	        sumoProcess = subprocess.Popen(['sumo', "-c", "./config/config"+suffix+".sumocfg"], stdout=log, stderr=log)

	        sumoProcess.wait()
                log.flush()
                log.close()
	        print "\n"
                
            counter += 1
print rank
start()
