import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
from natsort import natsorted

list_file = os.listdir("./output")

def table():
    print("File name\tTime\tmeanTravelTime")
    for fn in list_file:
        if 'summary' in  fn:
            #lines = open('./output/'+fn,'r').readlines()
            #xmldoc = minidom.parseString(lines[-2])
            #print(xmldoc.documentElement.tagName)
            tree = ET.parse('./output/'+fn)
            root = tree.getroot()
            print(fn + "\t" + root[-1].attrib['time'] + "\t" + root[-1].attrib['meanTravelTime'])
            #for child in root:
            #    print child.tag, child.attrib

def figure():
    graphs = []
    for fn in list_file:
        if "summary" in fn:
        #if fn == 'summary_S0.xml' or fn == 'summary_S1.xml':
        
            print(fn)
            tree = ET.parse('./output/'+fn)
            root = tree.getroot()
            x = []
            y = []
            for step in root:
               #print(float(step.attrib['time']))
               i = float(step.attrib['time'])
               x.append(i)
               y.append(float(step.attrib['meanTravelTime']))
            #graphs.append((x,y))
            line, = plt.plot(x,y,label=fn[8:-4])
            graphs.append(line)
                    #print len(x)
    print(len(graphs))
    #plt.plot(graphs[0][0],graphs[0][1],graphs[1][0],graphs[1][1])
    #lines = []
    #for graph in graphs:
    #    line, = plt.plot(graph[0],graph[1],label=fn[8:-4])
    #    lines.append(line)
    plt.axis([0,10000,0,1600])
    plt.ylabel('Mean Travel Time')
    plt.xlabel('Simulation Time')
    plt.legend(handles=graphs)
    plt.show()

def bargraph():
    labels = []
    total_time = []
    mean_tt = []
    data = {}
    for fn in list_file:
        if "summary" in fn:
            tree = ET.parse('./output/'+fn)
            root = tree.getroot()
            total_time.append(root[-1].attrib['time'])
            mean_tt.append(root[-1].attrib['meanTravelTime'])
            labels.append(fn[8:-4])
            data[fn[8:-4]] = (root[-1].attrib['time'],root[-1].attrib['meanTravelTime'])
    width = 0.45
    fig,ax = plt.subplots()
    ind = np.arange(len(labels))
    rects1 = ax.bar(ind,[data[key][0] for key in natsorted(data)],width,color='r')

    rects2 = ax.bar(ind+width,[data[key][1] for key in natsorted(data)],width,color='y')

    ax.set_ylabel('Time (seconds)')
    ax.set_xlabel('Simulation number')
    ax.set_xticks(ind+width)
    ax.set_xticklabels([key for key in natsorted(data)])
    ax.legend((rects1[0],rects2[0]),('Simulation Time','Mean Travel Time'))
    
    for i in range(len(rects1)):
        h1 = rects1[i].get_height()
        h2 = rects2[i].get_height()
        ax.text(rects1[i].get_x() +rects1[i].get_width()/2., h1+5,'%d' % int(h1), ha='center', va='bottom')
        ax.text(rects2[i].get_x() +rects2[i].get_width()/2., h2+5,'%d' % int(h2), ha='center', va='bottom')
         
    plt.show()


    
#figure()
bargraph()       

