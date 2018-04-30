

from os import listdir
import xml.etree.ElementTree as ET
import pandas as pd

def parse_deterministic():
    path = '../output/'
    files = listdir(path)
    with open(path+'det_results.csv','w') as f:
        for file in files:
            if 'summary_' in file:
                name = file.split('_')
                tree = ET.parse(path+file)
                root = tree.getroot()
                name = file.split('_')
                print(name)
                interval = 't1'
                if name[3] == '1000':
                    interval = 't2'
                elif name[3] == '2000':
                    interval = 't3'
                f.write("{}, {}, {}, {}\n".format(name[1], interval, root[-1].attrib['time'], root[-1].attrib['meanTravelTime']))
    

def parse_gt():
    path = '../results/combined/alpha2beta1/'
    files = listdir(path)
    with open(path+'gt_results.csv','w') as f:
        for file in files:
            if 'vulnerability' in file:
                name = file.split('_')
                print(name)
                interval = 't1'
                if name[2] == '1.csv':
                    interval = 't2'
                elif name[2] == '2.csv':
                    interval = 't3'
                df = pd.read_csv(path+file)
                vals = df.iloc[-1]
                for link in vals.axes[0][1:]:
                    f.write("{}, {}, {}\n".format(str(link).split("_")[0], interval, vals.loc[link]))
                    
    


if __name__ == '__main__':
    #parse_deterministic()
    parse_gt()