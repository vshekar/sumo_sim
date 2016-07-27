import os
import xml.etree.ElementTree as ET
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from natsort import natsorted

list_file = os.listdir("./output")
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
                names.append(name[0][0]+'to'+name[0][-1] + "\n" + interval_str)
                results[name[0][0]+'to'+name[0][-1] + "\n" + interval_str] = [float(root[-1].attrib['time']),float(root[-1].attrib['meanTravelTime'])]
                link_name.append(name[0][0]+'to'+name[0][-1])
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
    sns.set(font_scale=2.5)
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
    plt.ylim(0.8,1.2)
    #plt.tight_layout(h_pad=3)
    plt.show()

#table()
plot(table())
