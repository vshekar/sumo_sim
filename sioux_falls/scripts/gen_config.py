import random

class ConfigGen():
	def __init__(self, **kwargs):
		self.rerouters = kwargs['rerouters']
		self.intervals = kwargs['intervals']
		self.net_dict = kwargs['network']
		self.vul_edges = kwargs['vul_edges']
		self.sources = kwargs['sources']
		self.destinations = kwargs['destinations']

		
            	
	def generate(self):
		for edge in self.vul_edges:
			for interval in self.intervals:
				print(edge,interval)
				if type(edge) is not int and '--' in edge:
					self.suffix = '_' + str(edge[2:]) + '__' +str(interval[0]) + '_' +str(interval[1])
				else:
					self.suffix = '_' + str(edge) + '__' +str(interval[0]) + '_' +str(interval[1])
				self.generate_config()
				self.generate_additional(edge,interval)



	def generate_config(self):
		config_filepath = '../config/config'+self.suffix+'.sumocfg'
		f = open(config_filepath,'w')
		lines = ('<?xml version="1.0" encoding="UTF-8"?>\n'
		                '<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">\n'
		                '<input>\n'
		                        '<net-file value="../network/sf_net.net.xml"/>\n'
		                        '<route-files value="../trips/trip.xml"/>\n'
		                        '<additional-files value="additional'+ self.suffix +'.xml"/>\n'
		                '</input>\n'
		                '<output>\n'
		                        '<summary-output value="../output/summary'+ self.suffix + '.xml"/>\n'
		                '</output>\n'
		                '<report>\n'
		                        '<log value="../output/report'+ self.suffix +'.xml"/>\n'
		                '</report>\n'
		                '</configuration>\n'
		                )
		f.write(lines)
		f.close()


	def generate_additional(self,edge,interval):
		additional_filepath = '../config/additional'+self.suffix+'.xml'
		add_file = open(additional_filepath,'w')

		reroute_edges = ''
		for i,e in enumerate(self.rerouters[edge]):
			if i == 0:
				reroute_edges += str(e)
			else:
				reroute_edges += " " + str(e)

		#Begin defining TAZ 
		taz = ''

		#Parsing destination edges
		destinations = self.destinations
		            


		for i in range(len(destinations)):
		    taz += '<taz id="zone'+str(i)+'">\n'
		    for source in self.sources:
		    	taz += '<tazSource id="' + str(source) + '"/>\n'
		    taz += '<tazSink id="' + str(destinations[i]) + '"/>\n'
		    taz += '</taz>\n'
		#End defining TAZ

		lines = ('<additional>\n'
		                        + taz + 
		                        '<edgeData id="1" file="../output/edgeData'+ self.suffix +'.xml" begin="'+ str(self.intervals[0][0]) + '" end="'+ str(self.intervals[0][1]) + '"/>\n'
		                        '<edgeData id="2" file="../output/edgeData'+ self.suffix +'.xml" begin="'+ str(self.intervals[1][0]) + '" end="'+ str(self.intervals[1][1]) + '"/>\n'
		                        '<edgeData id="3" file="../output/edgeData'+ self.suffix +'.xml" begin="'+ str(self.intervals[2][0]) + '" end="'+ str(self.intervals[2][1]) + '"/>\n'
		                        '<edgeData id="4" file="../output/edgeData'+ self.suffix +'.xml" begin="'+ str(self.intervals[2][1]) + '" end="100000"/>\n'
		                '<rerouter id="1" edges="'+ reroute_edges +'">\n'
		                        '<interval begin="'+ str(interval[0]) +'" end="'+ str(interval[1]) +'">\n'
		                                '<closingReroute id="'+ str(edge) +'"/>\n' 
		                                
		                        '</interval>\n'
		                '</rerouter>\n'
		                '</additional>\n')
		add_file.write(lines)
		add_file.close()

	
	def generate_trips(self,total_cars=0):
		fl = '<?xml version="1.0"?>\n<trips>'
		st = ""
		curr_car = 0
		while curr_car < total_cars:
			st += '<trip id="%d" depart="%.2f" from="%s" to="%s"/>\n' % (curr_car, curr_car*2.0,random.choice(self.sources),random.choice(self.destinations))
			curr_car += 1
		
		fl += st
		fl += '</trips>'

		f = open('../trips/trip.xml','w')
		f.write(fl)