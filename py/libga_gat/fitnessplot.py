from canvasbase import CanvasBase2D
import numpy as np
from operator import itemgetter


class Fitnessplot(CanvasBase2D): 
    def __init__(self): 
        CanvasBase2D.__init__(self)
        self.filter_pareto_front = False

    def customize(self):
        self.axes.set_title("Fittest solution")
        self.axes.set_xlabel("Generation")
        self.axes.set_ylabel("Fitness / Objective value")

    def data_update(self, genome_info):
        ospace = genome_info["ospace"]
        fittest = min(enumerate(ospace), key=itemgetter(1))[0]
        self.data.set_xdata(np.append(self.data.get_xdata(), len(self.data.get_xdata())))
        self.data.set_ydata(np.append(self.data.get_ydata(), ospace[fittest]))
        self.axes.relim()
        self.axes.autoscale_view(True, True, True)
        self.fig.canvas.draw()

    def data_picker(self, data, mouseevent):
        return False, dict()
