# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 10:43:30 2017

@author: Shekar
"""
import pandas as pd

nominal = pd.read_csv('nominal.csv')
nominal = nominal.drop(nominal.columns[0], axis=1)
nominal['Nominal'] = nominal.Fuel.cumsum()


t1_disrupt = pd.read_csv('disrupted_0_3000_--12814#1.csv')
t1_disrupt = t1_disrupt.drop(t1_disrupt.columns[0], axis=1)
t1_disrupt['S1 at $\Delta t_1$'] = t1_disrupt.Fuel.cumsum()

t2_disrupt = pd.read_csv('disrupted_3000_6000_--12814#1.csv')
t2_disrupt = t2_disrupt.drop(t2_disrupt.columns[0], axis=1)
t2_disrupt['S1 at $\Delta t_2$'] = t2_disrupt.Fuel.cumsum()

t3_disrupt = pd.read_csv('disrupted_6000_9000_--12814#1.csv')
t3_disrupt = t3_disrupt.drop(t3_disrupt.columns[0], axis=1)
t3_disrupt['S1 at $\Delta t_3$'] = t3_disrupt.Fuel.cumsum()

total = pd.concat([nominal['Nominal'], t1_disrupt['S1 at $\Delta t_1$'], 
                   t2_disrupt['S1 at $\Delta t_2$'], 
                    t3_disrupt['S1 at $\Delta t_3$']], axis=1)
print(total.head())
total.plot()