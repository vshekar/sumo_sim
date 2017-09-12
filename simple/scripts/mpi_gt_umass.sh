#!/bin/bash

#BSUB-J sumo_sim
#BSUB-n 345
#BSUB-q long
#BSUB-W 120
#BSUB-e %J.err
#BSUB-R rusage[mem=1024]

source $HOME/.bashrc
mpirun -np 345 python 
