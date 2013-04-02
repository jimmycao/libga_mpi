# -*- coding: utf-8 -*-
# =============================================================================
# paretoplot3d.py
#
#
# displays a pareto plot with interactive picking for genome data 
# that has been saved using numpy, for instance
# np.savez(sys.argv[1], genome=alg.genome, ospace=alg.ospace
#      , fitnesses=alg.fitnesses)
# -----------------------------------------------------------------------------

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Paretoplot3D: 
    def __init__(self, genome_info): 
        self._genome = genome_info["genome"]
        self._ospace = genome_info["ospace"]
        self._fitnesses = genome_info["fitnesses"]

        if self._ospace.shape[1] < 3: 
            raise Exception("This plot is not suitable for less than 3D problems")
        if self._ospace.shape[1] > 3: 
            print("Warning: This optimization problem has more than three objectives. "
                  + "Only the first three are displayed for now. Change the "
                  + "paretoplot3d.py show() function.")

    def show(self):
        self._fig = plt.figure(1)
        rect = self._fig.patch
        rect.set_facecolor("white")
        self._ax  = self._fig.add_subplot(111, projection="3d")
        self._ax.set_title("Pareto Optimal Front")
        self._ax.set_xlabel("Objective #0")
        self._ax.set_ylabel("Objective #1")
        self._ax.set_zlabel("Objective #2")
        self._ax.scatter(self._ospace[:,0], self._ospace[:,1], self._ospace[:,2])
        plt.show()

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print 'usage: paretoplot3d.py <npz file>'
    else:
        plot = Paretoplot3D(np.load(sys.argv[1]))
        plot.show()
