from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class CanvasBase3D(FigureCanvas): 
    def __init__(self, parent=None, width=5, height=4, dpi=80): 
        self.parent = parent
        self.width  = width
        self.height = height
        self.dpi    = dpi

        plt.ion()

        self.fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        rect = self.fig.patch
        rect.set_facecolor("white")

        FigureCanvas.__init__(self, self.fig)
        self.axes = self.fig.add_subplot(111, projection="3d")

        self.setParent(self.parent)
        FigureCanvas.setSizePolicy(self
            , QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.clear()

    def clear(self):
        self.axes.cla()
        zeros = np.zeros((1, 3))
        self.data, = self.axes.plot(zeros[:,0], zeros[:,1], zeros[:,2], "ok")

        self.customize()
        
        self.fig.canvas.draw()

    def customize(self): 
        pass

