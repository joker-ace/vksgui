# coding=utf-8
__author__ = 'samorodok'
import heapq
import random
from collections import Counter

import networkx as nx


random.seed(None)
deviation = 250
nodesRem = 1


def attack(G, type=None):
    n = len(G)
    graph = G.copy()
    steps = 1
    largestComponent = list()
    averageComponent = list()
    percentRemNodes = list()
    listOfTargets = list()
    while True:
        if len(graph.edges()) == 0:
            percTreshold = percentRemNodes[get_percolation_threshold(largestComponent)]
            return steps, percTreshold, n, largestComponent, percentRemNodes, averageComponent, listOfTargets
        components = list(nx.connected_components(graph))
        components_length = map(len, components)
        largestComponent.append(len(components[0]))
        components_length.pop(0)
        if len(components_length) == 0:
            averageComponent.append(1)
        else:
            """
                size of average cluster = sum(number of size*size*size)/sum(number of size*size):
                http://iopscience.iop.org/1742-6596/297/1/012009/pdf/1742-6596_297_1_012009.pdf
            """
            ns = Counter()
            for lc in components_length:
                ns[lc] += 1
            numerator = 0
            denominator = 0
            for s in ns:
                numerator += s * s * ns[s]
                denominator += s * ns[s]
            averageComponent.append(float(numerator) / float(denominator))
        nodes = None
        if type == 'target':
            node_and_degree = graph.degree()
            nodes = heapq.nlargest(nodesRem, node_and_degree, key=lambda k: node_and_degree[k])  # max(node_and_degree, key = lambda k: node_and_degree[k])#
            listOfTargets.append(nodes[0])
        elif type == 'random':
            nodes = random.sample(graph.nodes(), nodesRem)
        graph.remove_nodes_from(nodes)
        percentRemNodes.append(float(steps * nodesRem) / n)
        steps += 1


def get_percolation_threshold(largestComponent):
    diffs = [
        largestComponent[i] - largestComponent[i + 1]
        for i in xrange(len(largestComponent) - 1)
    ]  # list of differences between two neighbors(components)
    return diffs.index(max(diffs))  # return index of max difference