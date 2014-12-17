__author__ = 'samorodok'
import community
import networkx as nx
# from igraph import Graph
import heapq
import pickle


def inputConvert():
    fdread = open('txtGraphs/Edges.csv', 'r')  #open .csv file
    fdWrite = open('edgeList.txt', 'w')  #open write file

    for line in fdread:  #for every line in csv file
        ids = line.split('\t')  #split line as tab
        ids[0] = int(ids[0])  #conversion 0-element to int
        ids[1] = int(ids[1])  #conversion 1-element to int
        fdWrite.write("{} {}\n".format(ids[0], ids[1]))  #write 0 and 1 elements to file
    fdread.close()  #close file
    fdWrite.close()  #close file

    fdRead = open('edgeList.txt', 'r')  #open file with edge list
    lines = fdRead.readlines()  #read all lines
    fdRead.close()  #close file

    G = nx.parse_edgelist(lines, nodetype=int)  #builte graph with edge list file
    nx.write_adjlist(G, 'adj_list.txt')  #write graph as adjacency matrix to file
    getPartitions(G)  #get partitions graph
    edgesInCommunitiesGraph('adj_list.txt', 'partitions.txt')  #add edges to graph of partitions


def convertToGraphML(graph, name):
    nx.write_graphml(graph, 'graphml/%s.graphml' % name)


def getIGraphCommunities(name):
    erd = Graph.Read_GraphML('graphml/%s.graphml' % name)
    erd = erd.as_undirected()
    #erd.write_graphml('%s.graphml'%name)
    #result = erd.community_edge_betweenness()
    result = erd.community_multilevel()
    fdWrite = open('txtGraphs/community_multilevel/%sPartitions.txt' % name, 'w')
    for i in xrange(len(result)):
        fdWrite.write("%d" % i)
        for node in result[i]:
            fdWrite.write(" %d" % node)
        fdWrite.write("\n")
    fdWrite.close()  #'''


def getPartitions(graph):
    partition = community.best_partition(graph)  #get partitions of graph
    fdWrite = open('partitions.txt', 'w')  #open file to write partitions
    for i in set(partition.values()):  #for every unique value in partition
        fdWrite.write("%d" % i)  #write value(number of community) to file
        members = [node for node in partition.keys() if partition[node] == i]  #list of keys(ids) that have value i
        # write all community members to file
        for memb in members:
            fdWrite.write(" %d" % int(memb))
        fdWrite.write("\n")
    fdWrite.close()


def edgesInCommunity(numberCommunity, graphName, communitiesName):
    #open files to write and to read
    fdGraph = open('%s' % graphName, 'r')
    fdCommunities = open('%s' % communitiesName, 'r')
    fdWrite = open('txtGraphs/%dCommunity.txt' % numberCommunity, 'w')
    #====================================
    neighbors = None
    #get community that have number = numberCommunity
    for line in fdCommunities:
        ids = list(map(int, line.split(' ')))
        if ids[0] == numberCommunity:
            neighbors = ids[1:]
            break
    #====================================
    for id in neighbors:  #for every id in chosen community
        fdGraph.seek(0, 0)  #set file pointer to begin of file
        fdWrite.write("%d" % id)  #write id from community to file
        for idS in fdGraph:  #for every line in graph file
            if not idS.startswith('#'):  #pass line that starts with '#'
                #find string that start with id from community
                idS = list(map(int, idS.split(' ')))
                if idS[0] == id:
                    #========================================
                    idS = idS[1:]
                    #all ids(neighbors) that equals (from graph file and community file) write to file
                    for node in idS:
                        if node in neighbors:
                            fdWrite.write(" %d" % node)
                    break
                    #==========================================
        fdWrite.write("\n")
    fdWrite.close()
    fdGraph.close()
    fdCommunities.close()


def edgesInCommunitiesGraph(graphName, communitiesName):  #same function but for hole graph
    fdGraph = open('%s' % graphName, 'r')
    fdCommunities = open('%s' % communitiesName, 'r')
    fdWrite = open('community.txt', 'w')
    for line in fdCommunities:
        ids = list(map(int, line.split(' ')))
        neighbors = ids[1:]
        for i in neighbors:
            fdGraph.seek(0, 0)
            fdWrite.write("%d" % i)
            for l in fdGraph:
                if not l.startswith('#'):
                    l = list(map(int, l.strip().split(' ')))
                    if l[0] == i:
                        l = l[1:]
                        for node in l:
                            if node in neighbors:
                                fdWrite.write(" %d" % node)
                        break
            fdWrite.write("\n")
    fdWrite.close()
    fdGraph.close()
    fdCommunities.close()


def printTargets(percTreshold, listOfTargets):
    i = 0
    fdWrite = open('targets.txt', 'w')
    while ( i < int(len(listOfTargets) * percTreshold)):
        fdWrite.write("{}. vk.com/id{}\n".format(i + 1, listOfTargets[i]))
        i += 1


def allFiles(groupName):
    fdRead = open('%s' % groupName, 'r')  #open file with edge list
    lines = fdRead.readlines()  #read all lines
    fdRead.close()  #close file

    G = nx.parse_edgelist(lines, nodetype=int)  #builte graph with edge list file
    nx.write_adjlist(G, 'adj_list.txt')  #write graph as adjacency matrix to file
    getPartitions(G)  #get partitions graph
    edgesInCommunitiesGraph('adj_list.txt', 'partitions.txt')  #add edges to graph of partitions