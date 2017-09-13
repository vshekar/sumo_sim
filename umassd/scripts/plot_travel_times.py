# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 12:00:27 2017

@author: Shekar
"""
import pandas as pd
import natsort

travel_times = pd.read_csv('travel_times.csv')
travel_times['Normalized'] = travel_times["Travel Time"]/travel_times.iloc[0]['Travel Time']
#print(travel_times.sort_index())
#print(travel_times.pivot(index="Scenario", columns="Delta", values="Travel Time"))
travel_times.pivot(index="Scenario", columns="Delta", values="Normalized").plot(kind='bar', ylim=(0.8, 1.5))