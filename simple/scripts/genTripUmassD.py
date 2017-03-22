#!/usr/bin/env python

import random

source_list1 = ['0to1','0to2']
dest_list1 = ['4to5','3to5']

source_list2 = ['5to3']
dest_list2 = ['1to0','2to0']

fl = '<?xml version="1.0"?>\n<trips>'

vph_up = [5,5,5,5,10,30,40,50,70,50,40,30,30,30,30,30,30,20,20,20,10,10,5,5]
#vph_up = [2*i for i in vph_up]

vph_down = [5,5,5,5,10,10,10,20,20,30,30,30,30,30,40,50,70,60,50,30,20,10,10,5]
#vph_down = [2*i for i in vph_down]

def trip_populate(vph,source_list,dest_list,depart_times,trips,curr_hour):
    for v in range(vph[curr_hour]):
        if depart_times[v] not in trips:
            trips[depart_times[v]] = [(random.choice(source_list),random.choice(dest_list))]
        else:
            trips[depart_times[v]].append((random.choice(source_list),random.choice(dest_list)))
    return trips
    
def gen_trips():
    total_time = 8640
    st = ""
    trip_id = 0

    trips = {}

    for i in range(24):
        lower_time = total_time*i/24
        upper_time = total_time*(i+1)/(24)
        
        depart_times = sorted([random.randint(lower_time,upper_time) for x in range(vph_up[i])])
        trips = trip_populate(vph_up,source_list1,dest_list1,depart_times,trips,i)

        depart_times = sorted([random.randint(lower_time,upper_time) for x in range(vph_down[i])])
        trips = trip_populate(vph_down,source_list2,dest_list2,depart_times,trips,i)
    
    for tt in sorted(trips):
        for line in trips[tt]:
            trip_id +=1
            st += '<trip id="%d" depart="%.2f" from="%s" to="%s"/>\n' % (trip_id, tt, line[0], line[1]) 
            
    return st

def gen_trips_new():
    tot_cars = 500
    curr_car = 0
    st = ""
    while curr_car < tot_cars:
        st += '<trip id="%d" depart="%.2f" fromTaz="%s" toTaz="%s"/>\n' % (curr_car, curr_car*1.0,'source','source')
        curr_car += 1
    return st

fl += gen_trips_new()
fl += '</trips>'

f = open('./trips/trip.xml','w')
f.write(fl)
