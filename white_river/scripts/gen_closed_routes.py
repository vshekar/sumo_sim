import sumolib

filenames = ['../Flood intersections/flood1.txt', '../Flood intersections/flood2.txt', '../Flood intersections/flood3.txt', '../Flood intersections/flood4.txt', '../Flood intersections/flood5.txt', '../Flood intersections/flood6.txt']

configfile = '../config/additional.xml'

config_str = '<additional>\n\
              <rerouter>\n\
              <interval begin="0" end="1000">\n'

network = sumolib.net.readNet('../wr_selected.net.xml')            

f = open(filenames[0],'r')
origIDs = []
for l in f:
    origIDs.append(l.rstrip())
    
all_edges = network.getEdges()
disabled_edges = []

for l in origIDs:
    for edge in all_edges:
        if l in edge.getID():
            disabled_edges.append(edge.getID())

for edge in disabled_edges:
    config_str += '<closingReroute id="{}"/>\n'.format(edge)

config_str += '</interval>\n</rerouter>\n</additional>'
o = open(configfile, 'w')
o.write(config_str)
