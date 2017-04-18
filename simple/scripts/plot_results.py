
import os
import xml.etree.ElementTree as ET
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#from natsort import natsorted

#list_file = os.listdir("./output")
sns.set(style="white", context="talk")



def table():
    print("File name\tTime\tmeanTravelTime")
    names = []
    sim_times = []
    link_name = []
    time_interval = []
    results = {}
    for fn in sorted(list_file):
        if 'summary' in  fn:
            #print fn
            tree = ET.parse('./output/'+fn)
            root = tree.getroot()
            
            print(fn + "\t" + "\t"  + root[-1].attrib['time'] + "\t" + root[-1].attrib['meanTravelTime'])
            name = fn[8:-4]
            if len(name) == 0:
                names.append("Full\nNetwork")
                fn_time = float(root[-1].attrib['time'])
                fn_mtt = float(root[-1].attrib['meanTravelTime'])
                #results["Full\nNetwork"] = [float(root[-1].attrib['time']),float(root[-1].attrib['meanTravelTime'])]
            else:
                name = name.split('_')
                interval_str = ""
                if int(name[2]) == 0:
                    interval_str = '$\Delta t1$'
                elif int(name[2]) == 500:
                    interval_str = '$\Delta t2$'
                elif int(name[2]) == 1000:
                    interval_str = '$\Delta t3$'
                names.append(name[0][0]+' to '+name[0][-1] + "\n" + interval_str)
                results[name[0][0]+' to '+name[0][-1] + "\n" + interval_str] = [float(root[-1].attrib['time']),float(root[-1].attrib['meanTravelTime'])]
                link_name.append(name[0][0]+' to '+name[0][-1])
                time_interval.append(interval_str)
                sim_times.append(float(root[-1].attrib['time']))
                
                #results[name[0][0] + "-" + name[0][-1]+ "\n" + interval_str]['mean_TT'] = float(root[-1].attrib['meanTravelTime'])
            
            #sim_times.append(float(root[-1].attrib['time']))
            #mean_TTs.append(float(root[-1].attrib['meanTravelTime']))
            #mergedlist = []
            #mergedlist.append(names[0])
            #mergedlist.extend(sorted(names[1:]))
    
    sim_times = [x/fn_time for x in sim_times]
    d = {'Link':link_name,'Interval':time_interval,'time':sim_times}
    df = pd.DataFrame(data=d)
    
    #return results,fn_time,fn_mtt
    return df

def plot(results):
    """
    fn_time = results[1]
    fn_mtt = results[2]
    results = results[0]
    names = []
    mean_TTs = []
    sim_times = []
    for name in sorted(results.keys()):
        names.append(name)
        sim_times.append(results[name][0]-fn_time)
        mean_TTs.append(results[name][0]/fn_time)
    """    
    
    #f, (ax2) = plt.subplots(1, 1, figsize=(8, 4), sharex=False)
    sns.set(font_scale=(3.5))
    f, (ax2) = plt.subplots(1, 1, sharex=False)
    
    #sns.barplot(names,sim_times,palette="Set3",ax=ax1)
    #ax1.set_ylabel('Simulation Time Difference')
    #ax1.grid(True, which='minor', color='b', linestyle='-')
    #ax1.grid(True)
    #sns.barplot(names,mean_TTs,palette="Set3",ax=ax2)
    sns.barplot(x='Link',y='time',hue='Interval',data=results,hue_order=['$\Delta t1$','$\Delta t2$','$\Delta t3$'],palette="muted")
    ax2.set_ylabel('Simulation Time/Nominal Time')
    ax2.set_xlabel('Disabled Link')
    ax2.grid(True)
    sns.despine(bottom=True)
    #plt.xticks(rotation=45)
    
    plt.setp(f.axes)
    plt.sca(f.axes[0])
    #plt.yticks(np.arange(1600, 1850, 50))
    #plt.ylim(1600,1850)
    #plt.sca(f.axes[1])
    #plt.yticks(np.arange(200, 320, 10))
    plt.ylim(1.0,1.12)
    #plt.tight_layout(h_pad=3)
    plt.show()

def plot_pollution(data):
    print len(data[0])
    #data = data[0]
    filenames = ['Nominal','$l_{2,4}$ at $\delta t_1$','$l_{2,4}$ at $\delta t_2$','$l_{2,4}$ at $\delta t_3$']
    styles = ['solid','dashed','dotted','dashdot']
    #print data
    sns.set(font_scale=1.5)
    sns.set_style("darkgrid")
    f, (ax2) = plt.subplots(1, 1, sharex=False)
    #sns.tsplot(time='Time Step',condition='Case',value='Pollution Amount',data=data)
    max_time = 0
    for i,dat in enumerate(data):
        plt.plot(dat[0],dat[1],label=filenames[i],linestyle=styles[i])
        if max(dat[0])>max_time:
            max_time = max(dat[0])
    plt.legend(bbox_to_anchor=(.05, 1), loc=2, borderaxespad=0.)
    ax2.set_ylabel('$CO_{2}$ released (Kg)')
    #ax2.set_ylabel('Fuel consumed (Liters)')
    ax2.set_xlabel('Time (seconds)')
    plt.xlim(0,max_time)
    plt.xticks(np.arange(0, max_time, 200))
    plt.savefig('out.pdf', bbox_inches='tight', pad_inches=0.05)
    #plt.show()

def extract_pollution(filenames):
    #cumul_pollution = np.zeros((2,), dtype=[('Time Step','i4'),('Pollution Amount','f4'),('Case','a25')]) 
    cumul_pollution = []
    for filename in filenames:
        tree = ET.parse(filename)
        root = tree.getroot()
        prev_total = 0
        poll = []
        time = []
        for i,interval in enumerate(root):
            if (interval.attrib['id']=="em1"):
                for edge in interval:
                    prev_total += float(edge.attrib['CO2_abs'])/1000000
                    #row = {'Time Step':float(interval.attrib['begin']),'Pollution Amount':prev_total,'Case':filename}
                    time.append(float(interval.attrib['begin']))
                    poll.append(prev_total)
        print filename + " : " + str(poll[-1])
        cumul_pollution.append([time,poll])
                    #rows.append(row)
    
    return cumul_pollution

def plot_num_veh(filenames):
    sns.set(font_scale=1.5)
    sns.set_style("darkgrid")
    f, (ax2) = plt.subplots(1, 1, sharex=False)
    labels = ['Nominal','$l_{2,4}$ at $\delta t_1$','$l_{2,4}$ at $\delta t_2$','$l_{2,4}$ at $\delta t_3$']
    styles = ['solid','dashed','dotted','dashdot']
    for f,filename in enumerate(filenames):
        num_veh = []
        tree = ET.parse(filename)
        root = tree.getroot()
        for i,step in enumerate(root):
            num_veh.append(int(step.attrib['running']))
        
        print labels[f] + " : " + str(np.trapz(num_veh))
        plt.plot(num_veh,label=labels[f],linestyle=styles[f])
    plt.legend(bbox_to_anchor=(.75, 1), loc=2, borderaxespad=0.)
    ax2.set_ylabel('Number of vehicles in the network')
    ax2.set_xlabel('Time (seconds)')
    plt.xticks(np.arange(0, 2000, 200))
    plt.savefig('out.pdf', bbox_inches='tight', pad_inches=0.05)
    #plt.show()

def plot_dist(filename):
    sns.set(font_scale=1.5)
    sns.set_style("darkgrid")
    f, (ax2) = plt.subplots(1, 1, sharex=False)
    tree = ET.parse(filename)
    root = tree.getroot()
    travel_times = []
    for i,tripinfo in enumerate(root):
    	travel_times.append(float(tripinfo.attrib['duration']))
    #sns.distplot(travel_times, hist=False, rug=True)
    ax2.hist(travel_times, 50)
    plt.savefig(filename+'.pdf', bbox_inches='tight', pad_inches=0.05)

    
#filenames = ['../output/edgeData.xml','../output/edgeData_2to4__0_500.xml','../output/edgeData_2to4__500_1000.xml','../output/edgeData_2to4__1000_1500.xml']
filenames = ['../output/summary.xml','../output/summary_2to4__0_500.xml','../output/summary_2to4__500_1000.xml','../output/summary_2to4__1000_1500.xml']
#filenames = ['../output/tripinfo.xml','../output/tripinfo_2_to_4_0_500.xml','../output/tripinfo_2_to_4_500_1000.xml','../output/tripinfo_2_to_4_1000_1500.xml']

#plot_pollution(extract_pollution(filenames))
#plot(table())
plot_num_veh(filenames)
#for filename in filenames:
#    print filename
#    plot_dist(filename)

    