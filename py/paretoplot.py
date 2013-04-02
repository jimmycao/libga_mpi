# -*- coding: utf-8 -*-
# =============================================================================
# paretoplot.py
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

class Paretoplot2D:
    def __init__(self, genome_info):
        self._genome = genome_info['genome']
        self._ospace = genome_info['ospace']
        self._fitnesses = genome_info['fitnesses']

        if self._ospace.shape[1] < 2:
            raise Exception('This plot is not suitable for 1D problems')
        if self._ospace.shape[1] > 2:
            print("Warning: This optimization problem has more than two "
                  + "objectives. Only the first two are displayed for now. "
                  + "Change the paretoplo.py show() function.")
        self._fig = plt.figure(1)
        rect = self._fig.patch
        rect.set_facecolor('white')
        self._ax = self._fig.add_subplot(1, 1, 1)
        self._ax.set_title('Pareto Optimal Front')
        self._ax.set_xlabel('Objective #0')
        self._ax.set_ylabel('Objective #1')
        self._fig.canvas.mpl_connect('pick_event', self.on_pick)

    def on_pick(self, event):
        if event.ind != None and len(event.ind) >= 1:
            print '''\r
Variables:\r
{0}\r
Objectives:\r
{1}\r
Fitness:\r
{2}'''.format(self._genome[event.ind[0]],
                    self._ospace[event.ind[0]],
                    self._fitnesses[event.ind[0]])

    def show(self):
        sc = plt.scatter(
            self._ospace[:, 0],
            self._ospace[:, 1],
            c=self._fitnesses,
            cmap=matplotlib.cm.get_cmap('gray'),
            s=40,
            picker=5,
            )
        plt.colorbar(sc)
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    if not len(sys.argv) == 2:
        print 'usage: paretoplot.py <npz file>'
    else:
        plot = Paretoplot2D(np.load(sys.argv[1]))
        plot.show()
