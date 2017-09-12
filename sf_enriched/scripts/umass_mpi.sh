#!/bin/bash

#BSUB -J sumo_sim
#BSUB -n 73
#BSUB -q long
#BSUB -W 2880
#BSUB -e %J.err
#BSUB -R rusage[mem=1024]

source $HOME/.bashrc
mpirun -np 73 python run_mpi.py
