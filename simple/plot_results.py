import os
import xml.etree.ElementTree as ET
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from natsort import natsorted

list_file = os.listdir("./output")
sns.set(style="white", context="talk")



def table():
	print("File name\tTime\tmeanTravelTime")
	names = []
	sim_times = []
	mean_TTs = []
	for fn in list_file:
		if 'summary' in  fn:
			tree = ET.parse('./output/'+fn)
			root = tree.getroot()
			
			print(fn + "\t" + "\t"  + root[-1].attrib['time'] + "\t" + root[-1].attrib['meanTravelTime'])
			name = fn[8:-4]
			if len(name) == 0:
				names.append("Full\nNetwork")
			else:
				name = name.split('_')
				interval_str = ""
				if int(name[2]) == 0:
					interval_str = 't1'
				elif int(name[2]) == 500:
					interval_str = 't2'
				elif int(name[2]) == 1000:
					interval_str = 't3'
				names.append(name[0][0] + "-" + name[0][-1]+ "\n" + interval_str)
			sim_times.append(float(root[-1].attrib['time']))
			mean_TTs.append(float(root[-1].attrib['meanTravelTime']))
			mergedlist = []
			mergedlist.append(names[0])
			mergedlist.extend(sorted(names[1:]))
			
	return mergedlist,sim_times,mean_TTs

def plot((names,sim_times,mean_TTs)):
	f, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
	
	sns.barplot(names,sim_times,palette="Set3",ax=ax1)
	ax1.set_ylabel('Total Simulation Time')
	#ax1.grid(True, which='minor', color='b', linestyle='-')
	ax1.grid(True)
	sns.barplot(names,mean_TTs,palette="Set3",ax=ax2)
	ax2.set_ylabel('Mean Travel Time')
	ax2.grid(True)
	sns.despine(bottom=True)
	#plt.xticks(rotation=20)
	
	plt.setp(f.axes)
	plt.sca(f.axes[0])
	plt.yticks(np.arange(1600, 1850, 50))
	plt.ylim(1600,1850)
	plt.sca(f.axes[1])
	plt.yticks(np.arange(200, 320, 10))
	plt.ylim(200,320)
	plt.tight_layout(h_pad=3)
	plt.show()
	
#table()
plot(table())