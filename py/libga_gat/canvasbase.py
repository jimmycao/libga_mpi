from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class CanvasBase2D(FigureCanvas): 
    def __init__(self, parent=None, width=5, height=4, dpi=80): 
        # save arguments
        self.parent = parent
        self.width  = width
        self.height = height
        self.dpi    = dpi

        # requred so that updating the plot works
        plt.ion()

        # create a figure with a white background
        self.fig = Figure(figsize=(self.width, self.height), dpi=self.dpi)
        rect = self.fig.patch
        rect.set_facecolor("white")
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)

        # Qt resizing 
        self.setParent(self.parent)
        FigureCanvas.setSizePolicy(self
            , QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.clear()

    def clear(self):
        self.axes.cla()
        self.axes.grid(True)
        zeros = np.zeros((1, 2))
        self.data, = self.axes.plot(zeros[:,0], zeros[:,1], "ok", picker=self.data_picker)

        # deriving classes will set titles, labels and appearance here
        self.customize()

        self.fig.canvas.mpl_connect("pick_event", self.data_picker)
        self.fig.canvas.draw()

    # handle picking, if required
    def data_picker(self):
        pass

    # set graph appearance
    def customize(self): 
        pass
