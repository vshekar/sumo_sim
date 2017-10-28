# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 12:42:17 2017

@author: Shekar
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

table = pd.read_csv('all_res.csv')
tau = pd.read_csv('tau_v5_0.csv')
vul = pd.read_csv('vulnerability_v3_0.csv')

label_size = 36
tick_size = 32

def draw_vul():
    plt.step(table['Iteration'], table['Mu'], linewidth=2.0)
    plt.xlim([1,95])
    plt.ylim([8,14])
    plt.xticks(np.arange(1,96,5), fontsize=tick_size)
    plt.yticks(fontsize=tick_size)
    plt.xlabel('Iteration', fontsize=label_size)
    plt.ylabel('System Vulnerability ($\mu$)', fontsize=label_size)
    plt.show()

def draw_delta_vul():
    plt.step(table['Iteration'], table['Delta mu'], linewidth=2.0)
    plt.xlim([1,95])
    plt.ylim([0,4])
    plt.xticks(np.arange(1,96,5), fontsize=tick_size)
    plt.yticks(fontsize=tick_size)
    plt.xlabel('Iteration', fontsize=label_size)
    plt.ylabel('Change in vulnerability ($\Delta \mu$)', fontsize=label_size)
    plt.show()

def draw_spearman():
    plt.step(table['Iteration'], table['Correlation'], linewidth=2.0)
    plt.xlim([1,95])
    plt.ylim([0,1])
    plt.xticks(np.arange(1,96,5), fontsize=tick_size)
    plt.yticks(fontsize=tick_size)
    plt.xlabel('Iteration', fontsize=label_size)
    plt.ylabel('Spearman\'s Rank Correlation', fontsize=label_size)
    plt.show()

def draw_tau():
    plt.plot(tau['Iteration'], tau['0to1'],':', linewidth=2.0, label='$L_{(0,1)}$')
    plt.plot(tau['Iteration'], tau['0to2'], linewidth=2.0, label='$L_{(0,2)}$')
    plt.plot(np.ones(95)*127.77, color='black', linewidth=0.5)
    plt.plot(np.ones(95)*135.64, color='black', linewidth=0.5)
    plt.xlim([1,95])
    plt.ylim([115,145])
    plt.xticks(np.arange(1,96,5), fontsize=tick_size)
    plt.yticks(fontsize=tick_size)
    plt.xlabel('Iteration', fontsize=label_size)
    plt.ylabel('MSA of s-expected link cost'+ r' ($\tau$)', fontsize=label_size)
    plt.legend(bbox_to_anchor=(0.8, 0.95), loc=2, borderaxespad=0., fontsize=tick_size)
    plt.show()
    #plt.savefig('tau.pdf', bbox_inches='tight')
    
def draw_link_vul():
    plt.plot(vul['Iteration'], vul['0to1'],':', linewidth=2.0, label='$L_{(0,1)}$')
    plt.plot(vul['Iteration'], vul['0to2'], linewidth=2.0, label='$L_{(0,2)}$')
    plt.xlim([1,95])
    plt.ylim([0,2.5])
    plt.xticks(np.arange(1,96,5), fontsize=tick_size)
    plt.yticks(fontsize=tick_size)
    plt.xlabel('Iteration', fontsize=label_size)
    plt.ylabel('Link Vulnerability ($\mu$)', fontsize=label_size)
    plt.legend(bbox_to_anchor=(0.80, 0.95), loc=2, borderaxespad=0., fontsize=tick_size)
    plt.show()
    
def draw_vul_avg():
    plt.step(table['Iteration'], table['Mu'], linewidth=2.0)
    plt.plot(table['Iteration'], table['Mu'].rolling(window=20, center=True).mean(), linewidth=5.0)
    plt.xlim([1,95])
    plt.ylim([8,14])
    plt.xticks(np.arange(1,96,4), fontsize=tick_size)
    plt.yticks(fontsize=tick_size)
    plt.xlabel('Iteration', fontsize=label_size)
    plt.ylabel('System Vulnerability ($\mu$)', fontsize=label_size)
    plt.show()

#draw_link_vul()
draw_tau()
#draw_spearman()
#draw_delta_vul()
#draw_vul_avg()
#draw_vul()