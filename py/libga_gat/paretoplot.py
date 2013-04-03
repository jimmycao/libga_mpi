from canvasbase import CanvasBase2D
import numpy as np


class Paretoplot2D(CanvasBase2D): 
    def __init__(self, pick_handler = None): 
        CanvasBase2D.__init__(self)
        self.filter_pareto_front = False
        self.pick_handler = pick_handler

    def customize(self):
        self.axes.set_title("Pareto optimal front")
        self.axes.set_xlabel("Objective #0")
        self.axes.set_ylabel("Objective #1")

    def redraw(self): 
        if self.filter_pareto_front:
            selection = np.asarray(self.fitnesses) < 1
            self.data.set_xdata(self.ospace[:,0][selection])
            self.data.set_ydata(self.ospace[:,1][selection])
        else:
            self.data.set_xdata(self.ospace[:,0])
            self.data.set_ydata(self.ospace[:,1])
        self.axes.relim()
        self.axes.autoscale_view(True, True, True)
        self.fig.canvas.draw()

    def data_update(self, genome_info): 
        self.ospace = genome_info["ospace"]
        self.fitnesses = np.asarray(genome_info["fitnesses"])
        self.genome = np.asarray(genome_info["genome"])
        self.redraw()

    def data_picker(self, data, mouseevent):
        if self.pick_handler != None and mouseevent.xdata != None:
            if self.filter_pareto_front:
                selection = np.asarray(self.fitnesses) < 1
                xdata  = self.ospace[:,0][selection]
                ydata  = self.ospace[:,1][selection]
                genome = self.genome[selection]
            else:
                xdata  = self.ospace[:,0]
                ydata  = self.ospace[:,1]
                genome = self.genome
            d = (xdata-mouseevent.xdata)**2 + (ydata-mouseevent.ydata)**2
            ind = min(range(len(xdata)), key = lambda x : d[x])
            self.pick_handler(self.genome[ind], [xdata[ind], ydata[ind]])
        return False, dict()
