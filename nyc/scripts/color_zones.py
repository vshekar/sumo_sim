import os
import subprocess
import sys
import random
from xml.sax.handler import ContentHandler

#sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import sumolib
from sumolib.visualization import helpers

import matplotlib.pyplot as plt
from optparse import OptionParser

def main():
    args = []
    optParser = OptionParser()
    optParser.add_option("-n", "--net", dest="net", metavar="FILE",
                         help="Defines the network to read")
    optParser.add_option("-i", "--selection", dest="selection", metavar="FILE",
                         help="Defines the selection to read")
    optParser.add_option("--selected-width", dest="selectedWidth",
                         type="float", default=1, help="Defines the width of selected edges")
    optParser.add_option("--color", "--selected-color", dest="selectedColor",
                         default='r', help="Defines the color of selected edges")
    optParser.add_option("--edge-width", dest="defaultWidth",
                         type="float", default=.2, help="Defines the width of not selected edges")
    optParser.add_option("--edge-color", dest="defaultColor",
                         default='#606060', help="Defines the color of not selected edges")
    optParser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                         default=False, help="If set, the script says what it's doing")
    helpers.addInteractionOptions(optParser)
    helpers.addPlotOptions(optParser)
    
    options, remaining_args = optParser.parse_args(args=args)
    
    net = sumolib.net.readNet('../network/nyc.net.xml')
    selections = []
    color_list = ['r','g','b','c','m','y','b']
    
    colors = {}
    widths = {}

    zone_path = '../network'
    zone_files = [os.path.join(zone_path,f) for f in os.listdir(zone_path) if 'zone' in f]
    print(zone_files)

    for zone in zone_files:
        selections.append(sumolib.files.selection.read(zone))

    for i,selection in enumerate(selections):
        for e in selection["edge"]:
            colors[e] = color_list[i%7]
            widths[e] = 0.5
    
    fig, ax = helpers.openFigure(options)
    ax.set_aspect("equal", None, 'C')
    helpers.plotNet(net, colors, widths, options)
    options.nolegend = True
    helpers.closeFigure(fig, ax, options)
    
main()