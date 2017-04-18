import sumolib
from sumolib.visualization import helpers
import xml.etree.ElementTree as ET
from optparse import OptionParser
import statistics



net = sumolib.net.readNet('../network/SF_with_TLS.net.xml')

tree = ET.parse('../output/edgeData.xml')
root = tree.getroot()

densities = []

density_vals = []
for interval in root:
	intv = {}
	for edge in interval:
		if 'density' in edge.attrib.keys():
			intv[edge.attrib['id']] = float(edge.attrib['density'])
			density_vals.append(intv[edge.attrib['id']])

	densities.append(intv)

print(statistics.median(sorted(density_vals)))


md = max(density_vals)

def get_color(value,max_density):
	hues = ['#47ff3a','#a9ff39', '#ffff38', '#ffbf37', '#ff8636', '#ff3535']
	#hues = ['#ff3535', '#ff8636', '#ffbf37', '#ffff38', '#a9ff39', '#47ff3a']
	step = max_density/len(hues)
	color = None
	for i in range(len(hues)):
		if i*step <= value <= (i+1)*step:
			color = hues[i]
			break
		else:
			color = hues[-1]
	return color


	

def normalize(value,max_density,min_density):
	return (value - min_density)/(max_density - min_density)


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

	for e in interval.keys():
		
		colors[e] = get_color(interval[e], md)
		#widths[e] = normalize(interval[e], max_density, min_density) + 2.0
		widths[e] = 2.0

	fig, ax = helpers.openFigure(options)
	ax.set_aspect("equal", None, 'C')
	helpers.plotNet(net, colors, widths, options)
	ax.set_title( '{num1:02d}:00:00 to {num2:02d}:00:00 hrs'.format(num1=(i+6)%24,num2=(i+7)%24))
	fig.savefig('../24 hour plot/hour'+str(i)+'.pdf', bbox_inches='tight',pad_inches=0)
	options.nolegend = True

	helpers.closeFigure(fig, ax, options)


