"""
This script compares the edges in zone#.txt to the edges in full_bridges.txt
If the edge is present in full_bridges, it is removed from the zone
"""


zone_fn = './network/zone'
bridge_fn = './network/full_bridges.txt'
bridges = []


with open(bridge_fn,'r') as f:
    for line in f:
        bridges.append(line)


for i in range(20):
    temp_list = []
    with open(zone_fn+str(i)+'.txt','r') as f:
        for line in f:
            if line not in bridges:
                temp_list.append(line)

    with open(zone_fn+str(i)+'.txt','w') as f:
        for line in temp_list:
            f.writelines(line)
print "Complete"
