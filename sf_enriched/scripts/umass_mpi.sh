#!/bin/bash

#BSUB -J sumo_sim
#BSUB -N 4
#BSUB -n 73
#BSUB -q long
#BSUB -W 600
#BSUB -o $HOME/%J.out
#BSUB -e $HOME/%J.err

source $HOME/.bashrc
mpirun python run_mpi.py
