__author__ = 'samorodok'
import numpy as np
import networkx as nx

# from enthought.mayavi import mlab
import matplotlib.pyplot as plt
import time
# from attacks import target_attack, random_attack

def draw(graph):
    start = time.time()
    print "Starting drawing"
    pos = nx.spring_layout(graph, dim=3)
    xyz = np.array([pos[v] for v in sorted(graph)])
    scalars = np.array(graph.nodes())
    mlab.figure(1, size=(1360, 768))
    mlab.clf()
    pts = mlab.points3d(xyz[:, 0], xyz[:, 1], xyz[:, 2],
                        scalars,
                        scale_factor=0.01,
                        scale_mode='none',
                        colormap='gist_heat',
                        resolution=15)
    pts.mlab_source.dataset.lines = np.array(graph.edges())
    tube = mlab.pipeline.tube(pts, tube_radius=0.001)
    mlab.pipeline.surface(tube, color=(0.6, 0.6, 0.6))
    print 'time draw: %.4f minutes' % ((float(time.time()) - float(start)) / 60.0)  #'''
    mlab.show()


def animation(graph, xyz, scalars, dirr):
    pos = nx.spring_layout(graph, dim=3)
    xyz = np.array([pos[v] for v in sorted(graph)])
    scalars = np.array(graph.nodes())
    mlab.figure(1, size=(1360, 768))
    mlab.clf()
    pts = mlab.points3d(xyz[:, 0], xyz[:, 1], xyz[:, 2],
                        scalars,
                        scale_factor=0.01,
                        scale_mode='none',
                        colormap='gist_heat',
                        resolution=15)
    pts.mlab_source.dataset.lines = np.array(graph.edges())
    tube = mlab.pipeline.tube(pts, tube_radius=0.001)
    mlab.pipeline.surface(tube, color=(0.7, 0.7, 0.7))

    @mlab.animate(delay=200)
    def anim():
        i = 0
        for g in target_attack(graph, xyz, scalars):
            if isinstance(g, tuple):
                break
            pts.mlab_source.dataset.lines = np.array(g.edges())
            tube = mlab.pipeline.tube(pts, tube_radius=0.001)
            mlab.pipeline.surface(tube, color=(0.85, 0.85, 0.85))
            mlab.savefig('%s/%d.png' % (dirr, i))
            i += 1
            yield

    anim()
    mlab.show()


def draw2D(G):
    plt.figure(figsize=(10, 10))
    pos = nx.pygraphviz_layout()
    nx.draw_networkx(G, pos=pos, with_labels=False, node_color='g',
                     node_size=100, alpha=0.5, width=0.7, edge_color='grey')
    plt.show()


def plot(resultsList):
    (y1, x1, y2) = resultsList[3:-1]  #[0]
    #(y3, x2, y4) = resultsList[1][3:-1]
    #(y3, x2, y4) = resultsList[3:-1]
    ax = plt.subplot(211)
    plt.plot(x1, y1, 'o', label='target attack')
    #plt.plot(x2, y3, '.', label = 'random attack')
    #plt.title('largestComponent_ta')
    plt.grid(True)
    #ax.legend()

    bx = plt.subplot(212)
    plt.plot(x1, y2, 'o', label='target attack')
    #plt.plot(x2, y4, '.', label = 'random attack')
    #plt.title('averageComponent_ta')
    plt.grid(True)
    #bx.legend(loc = 2)

    plt.show()