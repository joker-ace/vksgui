# coding=utf-8
__author__ = 'samorodok'
from draw import draw2D
from conversionTools import *
from attacks import attack

# inputConvert()#convertation from .csv to edge list .txt and get graph of communities with edges
graph = nx.read_adjlist('../members/lumen_phrases_common_friends.txt',
                        delimiter=' ')  #read matrix from file and create the graph

# draw2D(graph)
#print len(graph), nx.degree_pearson_correlation_coefficient(graph), nx.average_clustering(graph)#, nx.diameter(graph)#print info about the graph
#getPartitions(graph)
#edgesInCommunitiesGraph('ektor.txt','partitions.txt')
#G = nx.read_adjlist('adj_list.txt', delimiter=' ')
#G = nx.convert_node_labels_to_integers(graph)
#draw(G)
#G = nx.read_adjlist('community.txt', delimiter=' ')
#components = nx.connected_component_subgraphs(G)
#edgesInGroup('txtGraphs/samorodok_art_group_members_with_friends.txt')
#allFiles('kis.txt')
def run(args):
    return attack(*args)

if __name__ == '__main__':
    a = '''
    start = time.time()#
    print 'Starting attacks.'
    m.freeze_support()
    pool = m.Pool(2)#parallel modeling
    results = (pool.map(run,[(scaleFree, 'random'),(scaleFree, 'target')]))#
    pool.close()
    pool.join()
    print 'time: %.4f minutes'%((float(time.time())- float(start))/60.0)#print time''
    print ("Percolation threshold - %f" %results[1][1])
    printTargets(results[1][1], results[1][6])#print targets to file
    plot(results)#visualization of results'''

    results = attack(graph,'target')
    printTargets(results[1], results[6])
    #plot(results)#'''
