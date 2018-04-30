import sumolib
from sumolib.visualization import helpers

import matplotlib.pyplot as pyplot
from optparse import OptionParser

import pandas as pd

def plot(densities, md, net):
    args = []
    optParser = OptionParser()
    optParser.add_option("-n", "--net", dest="net", metavar="FILE",
                        help="Defines the network to read")
    optParser.add_option("--edge-width", dest="defaultWidth",
                        type="float", default=0.5, help="Defines the width of not selected edges")
    optParser.add_option("--edge-color", dest="defaultColor",
                        default='#000000', help="Defines the color of not selected edges")
    optParser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                        default=False, help="If set, the script says what it's doing")

    helpers.addInteractionOptions(optParser)
    helpers.addPlotOptions(optParser)
    options, remaining_args = optParser.parse_args(args=args)


    for i,interval in enumerate(densities):
        colors = {}
        widths = {}
        max_density = 0
        min_density = 10000
        for e in interval.keys():
            if max_density < interval[e]:
                max_density = interval[e]
            if min_density > interval[e]:
                min_density = interval[e]
        md = max_density

        for e in interval.keys():
            
            colors[e] = get_color(interval[e], md)
            #widths[e] = normalize(interval[e], max_density, min_density) + 2.0
            widths[e] = 2.0

        fig, ax = helpers.openFigure(options)
        ax.set_aspect("equal", None, 'C')
        helpers.plotNet(net, colors, widths, options)
        #ax.set_title( '{num1:02d}:00:00 to {num2:02d}:00:00 hrs'.format(num1=(i+6)%24,num2=(i+7)%24))
        ax.set_title('Iteration {}'.format(interval))
        fig.savefig('../results/combined/alpha1beta1/plots/iteration'+str(i)+'.pdf', bbox_inches='tight',pad_inches=0)
        options.nolegend = True

        helpers.closeFigure(fig, ax, options)


if __name__=="__main__":
    net = sumolib.net.readNet('../network/SF_with_TLS_combined.net.xml')
    density_file = pd.read_csv('../results/combined/alpha1beta1/densities_v5_0.xlsx')
    densities = density_file.to_dict(orient='records')
    #densities = []

    max_density = 0

    plot(densities, max_density, net)