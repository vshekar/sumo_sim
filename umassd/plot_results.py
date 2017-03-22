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
    name_map={'--12814#1':'$S_1$','--12814#2':'$S_2$','--12814#3':'$S_3$','--12814#4':'$S_4$','--12814#6':'$S_5$','--12814#7':'$S_6$','--12814#9':'$S_7$','--12814#10':'$S_8$','-12814#13':'$S_9$','-12814#14':'$S_{10}$','-12814#15':'$S_{11}$','-12814#16':'$S_{12}$'}
    for fn in natsorted(list_file):
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
                elif int(name[2]) == 3000:
                    interval_str = '$\Delta t2$'
                elif int(name[2]) == 6000:
                    interval_str = '$\Delta t3$'
                names.append(name[0] + "\n" + interval_str)
                results[name[0] + "\n" + interval_str] = [float(root[-1].attrib['time']),float(root[-1].attrib['meanTravelTime'])]
                link_name.append(name_map[name[0]])
                time_interval.append(interval_str)
                sim_times.append(float(root[-1].attrib['time']))
                
                #results[name[0][0] + "-" + name[0][-1]+ "\n" + interval_str]['mean_TT'] = float(root[-1].attrib['meanTravelTime'])
            
            #sim_times.append(float(root[-1].attrib['time']))
            #mean_TTs.append(float(root[-1].attrib['meanTravelTime']))
            #mergedlist = []
            #mergedlist.append(names[0])
            #mergedlist.extend(sorted(names[1:]))
    
    sim_times = [x/fn_time for x in sim_times]
    d = {'Link':link_name,'Interval':time_interval,'Time':sim_times}
    df = pd.DataFrame(data=d)
    df.sort_values('Link',inplace=True)
    
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
    sns.set(font_scale=3.5)
    f, (ax2) = plt.subplots(1, 1, sharex=False)
    
    #sns.barplot(names,sim_times,palette="Set3",ax=ax1)
    #ax1.set_ylabel('Simulation Time Difference')
    #ax1.grid(True, which='minor', color='b', linestyle='-')
    #ax1.grid(True)
    #sns.barplot(names,mean_TTs,palette="Set3",ax=ax2)
    row_order = ['$S_1$','$S_2$','$S_3$','$S_4$','$S_5$','$S_6$','$S_7$','$S_8$','$S_9$','$S_{10}$','$S_{11}$','$S_{12}$']
    sns.barplot(x='Link',y='Time',hue='Interval',data=results,hue_order=['$\Delta t1$','$\Delta t2$','$\Delta t3$'],palette="muted",order=row_order)
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
    plt.ylim(0.90,1.2)
    #plt.tight_layout(h_pad=3)
    plt.show()

#table()
plot(table())
