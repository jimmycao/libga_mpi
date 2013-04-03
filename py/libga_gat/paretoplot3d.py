from canvasbase3d import CanvasBase3D
import numpy as np


class Paretoplot3D(CanvasBase3D): 
    def __init__(self): 
        CanvasBase3D.__init__(self)
        self.filter_pareto_front = False

    def customize(self):
        self.axes.set_title("Pareto optimal front")
        self.axes.set_xlabel("Objective #0")
        self.axes.set_ylabel("Objective #1")
        self.axes.set_zlabel("Objective #2")

    def data_update(self, genome_info): 
        os = genome_info["ospace"][:,:3]
        if self.filter_pareto_front:
            selection = np.asarray(genome_info["fitnesses"]) < 1
            os = os[selection]
        self.data.remove()
        self.data, = self.axes.plot(os[:,0], os[:,1], os[:,2], "ok")
        self.fig.canvas.draw()
