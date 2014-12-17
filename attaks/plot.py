__author__ = 'samorodok'
import matplotlib.pyplot as plt


def plot(resultsList):
    (y1, x1, y2) = resultsList[3:-1]  # [0]
    # (y3, x2, y4) = resultsList[1][3:-1]
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