# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 16:51:16 2017

@author: shekar
"""
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

tree = ET.parse('../trips/trip.xml')
trips = tree.getroot()
#all_trips = []
all_trips = np.zeros((86400,), dtype=np.int)
for t in trips:
    #all_trips.append((t.attrib['id'],t.attrib['depart'],t.attrib['from'],t.attrib['to']))
    time = int(t.attrib['depart'])
    all_trips[time] += 1



plt.plot(moving_average(all_trips, 100))
plt.show()
