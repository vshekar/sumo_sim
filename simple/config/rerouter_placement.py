import networkx as nx

G = nx.DiGraph()

G.add_nodes_from([x for x in range(6)])

edges = [(0,1),(1,0),(0,2),(2,0),(1,2),(1,3),(2,4),(4,2),(4,3),(3,4),(3,5),(5,3),(4,5)]

G.add_edges_from(edges)

for edge in edges:
	G[edge[0]][edge[1]]['name'] = str(edge[0])+'to'+str(edge[1])
	
for edge in G.edges_iter():
	if G[edge[0]][edge[1]]['name'] == "4to5":
		#print "Found it!"
		for e in G.in_edges(edge[0]):
			print str(e[0])+ 'to' + str(e[1])