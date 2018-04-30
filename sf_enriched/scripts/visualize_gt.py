import sumolib
from sumolib.visualization import helpers

import matplotlib.pyplot as pyplot
from optparse import OptionParser

import pandas as pd
import re 
import imageio
import os

def plot(densities, md, net, path):
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
                #print(interval)
                max_density = interval[e]
            if min_density > interval[e]:
                min_density = interval[e]
        
        for e in interval.keys():
            if 'Unnamed' not in e:
                col, wid = get_color(interval[e], max_density, min_density)           
                colors[e] = col
                #widths[e] = normalize(interval[e], max_density, min_density) + 2.0
                widths[e] = wid

        fig, ax = helpers.openFigure(options)
        ax.set_aspect("equal", None, 'C')
        helpers.plotNet(net, colors, widths, options)
        #ax.set_title( '{num1:02d}:00:00 to {num2:02d}:00:00 hrs'.format(num1=(i+6)%24,num2=(i+7)%24))
        ax.set_title('Iteration {}'.format(i))
        fig.savefig(path+'plots/densities/iteration'+str(i)+'.png', bbox_inches='tight',pad_inches=0)
        #options.nolegend = True

        #helpers.closeFigure(fig, ax, options)
        #fig.close()

def get_color(value,max_density, min_density):
    hues = ['#47ff3a','#a9ff39', '#ffff38', '#ffbf37', '#ff8636', '#ff3535']
    #hues = ['#ff3535', '#ff8636', '#ffbf37', '#ffff38', '#a9ff39', '#47ff3a']
    #print(max_density, min_density)
    step = (max_density-min_density)/len(hues)
    color = hues[0]
    width = 1
    for i in range(len(hues)):
        if i*step <= value <= (i+1)*step:
            color = hues[i]
            width = i+1
            break
        else:
            color = hues[-1]
            width = len(hues)
    return color, width

def sorted_nicely( l ): 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)

def create_gif(filenames, path):
    frames = []
    for filename in filenames:
        image = imageio.imread(path+ 'plots/densities/'+ filename)
        frames.append(image)
    
    imageio.mimsave(path+'den_anim.gif', frames, 'GIF', duration=1)
    




if __name__=="__main__":
    net = sumolib.net.readNet('../network/SF_with_TLS_combined.net.xml')
    #density_file = pd.read_csv('../results/combined/alpha1beta1/densities_v5_0.csv')
    path = '../results/combined/alpha2beta1/'
    density_file = pd.read_csv(path + 'densities_v5_0.csv')
    density_file = density_file.drop('Unnamed: 0', 1)
    densities = density_file.to_dict(orient='records')
    #print(densities[0])
    #densities = []
    max_density = 0
    plot(densities, max_density, net, path)
    
    files = os.listdir(path + 'plots/densities/')
    files = sorted_nicely(files)

    create_gif(files, path )