
import csv
import scipy.stats.mstats
import numpy as np
from statistics import mean, median

f = open('sim_time.csv', 'r')
r = open('vul.csv', 'r')
time_reader = csv.reader(f, delimiter=',')
rho_reader = csv.reader(r, delimiter=',')

total_corr = []
total_pval =[]
count = 0

for i, t in enumerate(time_reader):
    
    #for rho in rho_reader:
    
    rho = next(rho_reader)
    time_list = list(map(float, t[1:]))
    rho_list = list(map(float, rho[1:]))
    #print(rho_list)
    res = scipy.stats.mstats.spearmanr(rho_list, time_list, use_ties = False)
    #res2 = scipy.stats.mstats.pearsonr(rho_list, time_list)
    #print(type(float(res.correlation)))
    #print(i, float(res.correlation), float(res.pvalue))
    
    #if float(res.correlation) > 0:
        #print(res.correlation)
    count += 1
    total_corr.append(float(res.correlation))
    total_pval.append(float(res.pvalue))
        
print(mean(total_corr), mean(total_pval))
print(median(total_corr), median(total_pval))
        
