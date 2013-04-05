from canvasbase3d import CanvasBase3D
import numpy as np


class Paretoplot3D(CanvasBase3D): 
    def __init__(self, obj1 = 1, obj2 = 2, obj3 = 3): 
        self.obj1 = obj1
        self.obj2 = obj2
        self.obj3 = obj3
        self.filter_pareto_front = False
        CanvasBase3D.__init__(self)

    def customize(self):
        self.axes.set_title("Pareto optimal front")
        self.axes.set_xlabel("Objective #" + str(self.obj1))
        self.axes.set_ylabel("Objective #" + str(self.obj2))
        self.axes.set_zlabel("Objective #" + str(self.obj3))

    def data_update(self, genome_info): 
        os = genome_info["ospace"]
        if self.filter_pareto_front:
            selection = np.asarray(genome_info["fitnesses"]) < 1
            os = os[selection]
        self.data.remove()
        self.data, = self.axes.plot(os[:,self.obj1] \
                                  , os[:,self.obj2], os[:,self.obj3], "ok")
        self.fig.canvas.draw()
