#!/usr/bin/env python

import random

source_list = ['--12805','-12790','-12811','-12808','-12797','--12786#2','--12816','-12798']

dest_list = ['-12826']

fl = '<?xml version="1.0"?>\n<trips>'


def gen_trips():
    tot_time = 3600
    curr_time = 0
    st = ""
    while curr_time < tot_time:
        st += '<trip id="%d" depart="%.2f" from="%s" to="%s"/>\n' % (curr_time, curr_time*1.0,random.choice(source_list),random.choice(dest_list))
        curr_time += 1
    return st

fl += gen_trips()
fl += '</trips>'

f = open('trip.xml','w')
f.write(fl)
