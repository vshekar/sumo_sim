#!/bin/bash

#SBATCH -A rendezvous
#SBATCH -t 10
#SBATCH -N 3
#SBATCH -n 58 
#SBATCH -J sumo_sim
#SBATCH -o /people/shek628/shekar_%j.out
#SBATCH -e /people/shek628/shekar_%j.err

#source /etc/profile.d/modules.csh
module purge
#module load pnnl_env
source /people/shek628/.bashrc
ulimit

echo
echo "loaded modules"
echo
module list >& _modules.lis_
cat _modules.lis_
/bin/rm -f _modules.lis_
echo
echo limits
echo
ulimit -a
echo
echo "Environment Variables"
echo
printenv
echo
echo "ldd output"
echo
mpirun -np 58 python run_mpi.py 

