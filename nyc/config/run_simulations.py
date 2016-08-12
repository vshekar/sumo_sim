
def chunk_gen(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def write_zone(lst,i):
    f = open('../network/zone'+str(i)+'.txt','w')
    for link in lst:
        f.write('edge:'+link+'\n')
    f.close()


def get_sources():
    sources = []
    f = open('../network/Manhattan.txt','r')
    for line in f.readlines():
        if 'edge' in line:
            sources.append(line[5:])
    #print(len(sources))
    #print sources[-1]
    link_lists = chunk_gen(sources, 20)
    for i in range(20):
        write_zone(next(link_lists),i)
        


get_sources()
