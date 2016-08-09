from mpi4py import MPI
import subprocess

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
#f = open('rank'+str(rank),'w')
#f.writelines('My rank is : ' + str(rank))
#f.close()

def start():
    suffix = ""
    #vul_edges = ['4to5','3to5','3to4','1to3','2to4','1to2','0to1','0to2']
    vul_edges = {'--12814#1':['--12805','--12814#2'],'--12814#2':['-12790','--12814#3'],'--12814#3':['-12811','--12814#4'],'--12814#4':['--12814#5','--12821'],'--12814#6':['--12814#7','-12801#1'],'--12814#7':['-12797','--12814#8'],'--12814#9':['-12804','--12814#10'],'--12814#10':['-12782','--12814#11'],'-12814#13':['-12770','-12814#12'],'-12814#14':['--12786#0','-12814#13'],'-12814#15':['--12816','-12814#14'],'-12814#16':['-12798','-12814#15']}
    #dest_edges = ['4to5','3to5']
    intervals = [(0,3000),(3000,6000),(6000,9000)]
    counter = 0
    for edge in vul_edges.items():
        for interval in intervals:
            if rank == counter:
                log = open("log"+str(rank),'w')
                suffix = '_' + edge[0] + '__' +str(interval[0]) + '_' +str(interval[1])
                #generate_config(edge,interval,suffix)
                #generate_additional(edge,G,interval,intervals,suffix)
                #print suffix +'\n'
                sumoProcess = subprocess.Popen(['sumo',"--time-to-teleport","-1", "-c", "/people/shek628/sim/umassd/config/config"+suffix+".sumocfg"], stdout=log, stderr=log)
                sumoProcess.wait()
                log.flush()
                log.close()
            counter += 1

    print rank

start()
