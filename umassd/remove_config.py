import os

files = os.listdir("./output")
for f in files:
    if 'summary' in f:
        with open('./output/'+f,'r') as fin:
            data = fin.readlines()
        with open('./output/'+f,'w') as fout:
            fout.writelines(data[:1] + data[3:])

