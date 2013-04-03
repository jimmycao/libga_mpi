#!/usr/bin/env python

import sys
import os
import imp
import logging
import pickle
import time

from PyQt4 import QtGui, QtCore, uic, QtWebKit

from fitnessplot import Fitnessplot    #1d
from paretoplot import Paretoplot2D    #2d
from paretoplot3d import Paretoplot3D  #3d
import optimizationprocess

import numpy as np


class LineEditLogger(logging.Handler): 
    def __init__(self, dest): 
        self.dest = dest
        logging.Handler.__init__(self)
        
    def emit(self, record):
        if record.levelno == logging.INFO:             
            self.dest.append("[{0}] {1}".format(\
              time.strftime("%H:%M:%S", time.gmtime()), record.msg))
            return
        if record.levelno == logging.ERROR:
            self.dest.append("<p style=\"color:red\">[{0}] {1}</p>".format(\
              time.strftime("%H:%M:%S", time.gmtime()), record.msg))


class LibgaGAT(QtGui.QMainWindow): 

    # signal is emitted when this instance receives
    # a logging record from the host thread. it is connected
    # to self.on_logging_record which updates the UI. 
    logging_record_trigger = QtCore.pyqtSignal(str)
    data_update_trigger = QtCore.pyqtSignal(str)

    def __init__(self, parent = None):
        super(LibgaGAT, self).__init__(parent)
        uic.loadUi("libga_gat.ui", self)
        
        # add our "ready" widget to the status bar
        self.ready_panel = QtGui.QLabel()
        self.statusBar().addWidget(self.ready_panel)
        self.set_ready(False)

        # add a progress bar to the status bar
        self.progress = QtGui.QProgressBar()
        self.progress.setStyleSheet("min-width:360px;max-width:360px")
        self.progress.hide()
        self.statusBar().addWidget(self.progress)

        # add command button to the status bar 
        self.abort_button = QtGui.QCommandLinkButton("Abort optimization")
        self.abort_button.hide()
        self.statusBar().addWidget(self.abort_button)
        self.abort_button.connect(self.abort_button
            , QtCore.SIGNAL("clicked()")
            , self.on_abort_button_clicked)

        # display help page
        self.browser.load(QtCore.QUrl("html/index.html"))
        self.browser.page().setLinkDelegationPolicy(
            QtWebKit.QWebPage.DelegateAllLinks)
        self.browser.connect(self.browser
            , QtCore.SIGNAL("linkClicked(QUrl)")
            , self.on_browser_link_clicked)

        # set header titles in properties pane (graph pick results)
        self.objectives_list.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("value"))
        self.variables_list.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("value"))

        # just an initial empty plot
        plot_layout = QtGui.QVBoxLayout()
        self.plot_1 = Fitnessplot()
        self.plot_2 = Paretoplot2D(self.on_plot_2_picked)
        self.plot_3 = Paretoplot3D()
        plot_layout.addWidget(self.plot_1)
        plot_layout.addWidget(self.plot_2)
        plot_layout.addWidget(self.plot_3)
        self.plot_area.setLayout(plot_layout)
        self.show_plot_1d()

        # logger that displays messages in the UI 's output pane
        self.logger = logging.getLogger("libga_gat")
        self.logger.addHandler(LineEditLogger(self.output))
        self.logger.setLevel(logging.INFO)

        # since the host for our compute process is running in its own 
        # thread we need signals to trigger UI updates
        self.logging_record_trigger.connect(self.on_logging_record)
        self.data_update_trigger.connect(self.on_data_update)

    def on_abort_button_clicked(self):
        self.server.abort_process()
        self.progress.hide()
        self.abort_button.hide()

    def on_plot_2_picked(self, picked_variables, picked_ospace): 
        if len(picked_variables) > 0 and len(picked_ospace) > 0:
            self.objectives_list.setColumnCount(1)
            self.objectives_list.setRowCount(len(picked_ospace))
            for i in range(len(picked_ospace)): 
                self.objectives_list.setItem(i, 0, QtGui.QTableWidgetItem(\
                    QtCore.QString("{0}".format(picked_ospace[i]))))
            self.objectives_list.resizeColumnsToContents()

            self.variables_list.setColumnCount(1)
            self.variables_list.setRowCount(len(picked_variables))
            for i in range(len(picked_variables)): 
                self.variables_list.setItem(i, 0, QtGui.QTableWidgetItem(\
                    QtCore.QString("{0}".format(picked_variables[i]))))
            self.variables_list.resizeColumnsToContents()

    def load_example_rastrigin_6(self):
        self.objectives.setValue(1)
        self.variables.setValue(4)
        self.constraints_min_max_checked(True)
        self.constraints_min.setText("-5.12")
        self.constraints_max.setText("+5.12")
        self.module.setText("../test_problems.py")
        self.function.setText("rastrigin_6")

    def load_example_kursawe(self): 
        self.objectives.setValue(2)
        self.variables.setValue(4)
        self.constraints_min_max_checked(True)
        self.constraints_min.setText("-5")
        self.constraints_max.setText("+5")
        self.module.setText("../test_problems.py")
        self.function.setText("kursawe")

    def load_example_MOP5(self): 
        self.objectives.setValue(3)
        self.variables.setValue(2)
        self.constraints_min_max_checked(True)
        self.constraints_min.setText("-30")
        self.constraints_max.setText("+30")
        self.module.setText("../test_problems.py")
        self.function.setText("MOP5")
        
    def on_browser_link_clicked(self, url):
        url = str(url.path())
        if "libga_gat://" in url:
            if "load_example_rastrigin_6" in url: 
                self.load_example_rastrigin_6()
                return
            if "load_example_kursawe" in url: 
                self.load_example_kursawe()
                return
            if "load_example_MOP5" in url: 
                self.load_example_MOP5()
                return

    # fitness plot for 1d problems
    def show_plot_1d(self):
        self.plot_1.show()
        self.plot_2.hide()
        self.plot_3.hide()

    # just a simple initial (empty) 2d plot to give the user
    # a clue of what to expect
    def show_plot_2d(self):
        self.plot_1.hide()
        self.plot_2.show()
        self.plot_3.hide()

    # pareto plot for 3d problems
    def show_plot_3d(self): 
        self.plot_1.hide()
        self.plot_2.hide()
        self.plot_3.show()

    # if all data has been entered correctly the 
    # application is "ready". display that information in the status bar. 
    def set_ready(self, ready):
        if ready: 
            self.ready_panel.setText("Ready - Start with Menu: Optimization > Run")
            self.ready_panel.setStyleSheet(
                "QLabel {background-color:blue;min-width:360px;"
                + "max-width:360px;padding-left:5px;"
                + "color:white}")
        else:
            self.ready_panel.setText("Not ready")
            self.ready_panel.setStyleSheet(
                "QLabel {background-color:orange;min-width:360px;"
                + "max-width:360px;padding-left:5px;"
                + "color:white}")
            
    # display a question before closing the application
    def closeEvent(self, event): 
        reply = QtGui.QMessageBox.question(self
           , "Libga GAT", "Are you sure you want to quit?"
           , QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes: 
            event.accept()
        else:
            event.ignore()

    def copy_to_clipboard(self): 
        if self.objectives_list.rowCount() > 0: 
            ret = ""
            for i in range(self.objectives_list.rowCount()):
                ret = ret + str(self.objectives_list.item(i,0).text()) + " "
            ret = ret + "\r\n"
            for i in range(self.variables_list.rowCount()): 
                ret = ret + str(self.variables_list.item(i,0).text()) + " "
            QtGui.QApplication.clipboard().setText(ret)

    def filter_pareto_plot_checked(self, checked): 
        self.plot_2.filter_pareto_front = checked
        self.plot_2.redraw()

    def select_python_module(self): 
        module = QtGui.QFileDialog.getOpenFileName(self, "Select Python module", ".")
        self.module.setText(module)

    def select_constraints_file(self): 
        constraints = QtGui.QFileDialog.getOpenFileName(self, "Select constraints file", ".")
        self.constraints_file.setText(constraints)

    def population_changed(self, population): 
        self.elite.setMaximum(population)
        self.archive.setMaximum(population)

    # doesn't actually load the test problem module. that is
    # verified when the user actually wants to run the optimizion. 
    def check_ready(self): 
        ready = self.module.text() != "" and self.function.text() != "" \
            and os.path.exists(self.module.text()) \
            and self.elite.value() < self.population.value() \
            and self.archive.value() < self.population.value()
        self.set_ready(ready)
        self.actionRun.setEnabled(ready)
        return ready

    # some settings only make sense for one-dimensional 
    # or two-dimensional problems. 
    def objectives_changed(self, objectives): 
        if objectives == 1: 
            self.archive.setEnabled(False)
            self.elite.setEnabled(True)
            self.selection.setEnabled(True)
            self.view_frame_0.setEnabled(False)
            self.view_x_axis.setEnabled(False)
            self.view_x_axis_label.setEnabled(False)
            self.view_y_axis.setEnabled(False)
            self.view_y_axis_label.setEnabled(False)
            self.view_z_axis_check.setEnabled(False)
            self.view_z_axis.setEnabled(False)
            self.filter_pareto_front.setEnabled(False)
            self.show_plot_1d()
            self.plot_selection_label.setText("FITTEST")
        else:
            self.archive.setEnabled(True)
            self.elite.setEnabled(False)
            self.selection.setEnabled(False)
            self.view_frame_0.setEnabled(True)
            self.view_x_axis.setEnabled(True)
            self.view_x_axis_label.setEnabled(True)
            self.view_y_axis.setEnabled(True)
            self.view_y_axis_label.setEnabled(True)
            self.view_z_axis_check.setEnabled(objectives > 2)
            self.view_z_axis.setEnabled(objectives > 2 \
                 and self.view_z_axis_check.checkState())
            self.filter_pareto_front.setEnabled(True)
            if objectives == 2: 
                self.show_plot_2d()
            else:
                self.show_plot_3d()
            self.plot_selection_label.setText("SELECTION")

    def constraints_min_max_checked(self, checked): 
        if checked: 
            self.radioButton_2.setChecked(False)
            self.constraints_min.setEnabled(True)
            self.constraints_max.setEnabled(True)
            self.constraints_file.setEnabled(False)
            self.select_constraints_file_btn.setEnabled(False)

    def constraints_from_file_checked(self, checked): 
        if checked:
            self.radioButton.setChecked(False)
            self.constraints_file.setEnabled(True)
            self.constraints_min.setEnabled(False)
            self.constraints_max.setEnabled(False)
            self.select_constraints_file_btn.setEnabled(True)

    def module_changed(self, module): 
        self.check_ready()

    def function_changed(self, module): 
        self.check_ready()

    def view_z_axis_checked(self, checked): 
        self.view_z_axis.setEnabled(checked)

    # return the constraints for the selected problem in form of a 
    # numpy matrix - doesn't matter if constraints have been specified via
    # numpy text file or min and max values in the UI. 
    def constraints_matrix(self): 
        assert self.check_ready()
        if self.radioButton.isChecked(): 
            minval = self.constraints_min.text().toFloat()[0]
            maxval = self.constraints_max.text().toFloat()[0]
            variables = self.variables.value()
            return np.asarray([minval, maxval]*variables).reshape((variables, 2))
        else:
            filename = str(self.constraints_file.text())
            c = np.loadtxt(filename)
            if c.shape != [variables, 2]: 
                self.logger.info("Constraints file has the wrong shape. Must be a matrix "
                + "of type (variables x 2)")
                return None
            return c

    # received a logging record. forward that to our instance logger. 
    # this has been triggered by a signal and is running in the UI thread.
    def on_logging_record(self, contents): 
        msg = pickle.loads(str(contents))
        if msg.levelno == logging.INFO: 
            self.logger.info(msg.msg)
            return
        if msg.levelno == logging.ERROR:
            self.logger.error(msg.msg)

    # received a new genome (new generation) from the optimization process. 
    # this has been triggered by a signal and is running in the UI thread. 
    def on_data_update(self, contents):
        self.progress.setValue(self.progress.value() + 1)
        genome_info = pickle.loads(str(contents))

        if self.objectives.value() == 1:
            # update info in the properties pane next
            # to the plot
            ospace = genome_info["ospace"]
            fittest_index = min(enumerate(ospace))[0]
            fittest = genome_info["genome"][fittest_index]

            self.objectives_list.setRowCount(1)
            self.objectives_list.setItem(0,0, QtGui.QTableWidgetItem(\
               QtCore.QString("{0}".format(ospace[fittest_index]))))
            self.objectives_list.resizeColumnsToContents()

            self.variables_list.setRowCount(len(fittest))
            for i in range(len(fittest)):
                self.variables_list.setItem(i, 0, QtGui.QTableWidgetItem(\
                    QtCore.QString("{0}".format(fittest[i]))))
            self.variables_list.resizeColumnsToContents()

            # plot new data
            self.plot_1.data_update(genome_info)
        else:
            plot = self.plot_2 if self.objectives.value() == 2 else self.plot_3
            plot.filter_pareto_front = self.filter_pareto_front.checkState()
            plot.data_update(genome_info)

        # if we are done, then hide status bar and abort button
        if self.progress.value() == self.generations.value():
            self.progress.hide()
            self.abort_button.hide()

    # start a host thread and a compute process 
    def run_optimization(self): 
        if not self.check_ready(): 
            self.logger.error("Libga GAT is NOT ready. Check settings")
            return

        # try to load module
        mod_name = os.path.split(str(self.module.text()))[1]
        try: 
            base = os.path.splitext(mod_name)[0]
            mod = imp.load_source(base, str(self.module.text()))
        except Exception as ex:
            self.logger.error("Failed to load module " + str(self.module.text()))
            self.logger.error("with exception " + str(ex))
            return

        # check if objective function exists
        if not hasattr(mod, str(self.function.text())):
            self.logger.error("Module has no function named " + str(self.function.text()))
            return

        # get a constraints matrix. this is None if the constraints file
        # has the wrong shape. an error message has already been logged
        # in this case.
        constraints = self.constraints_matrix()
        if constraints == None: 
            return

        # show appropriate plot based on number of objectives. 
        # doesn't create a new plot instance, but resets view.
        if self.objectives.value() == 1: 
            self.plot_1.clear()
            self.show_plot_1d()
        else:
            if self.objectives.value() == 2: 
                self.plot_2.clear()
                self.show_plot_2d()
            else:
                if self.objectives.value() > 2:
                    self.plot_3.clear()
                    self.show_plot_3d()

        # a few changes in the UI for when the optimization is running
        self.tabWidget.setCurrentIndex(1)
        self.progress.setMinimum(0)
        self.progress.setMaximum(self.generations.value())
        self.progress.setValue(0)
        self.progress.show()
        self.abort_button.show()

        # create the optimization process which actually is executing the test
        # functions. ensures that the GUI won't crash if the tested objective 
        # function has a fault.
        self.logger.info("Starting optimization process")
        # call a helper function which starts the process and returns a 
        # server object wihch can communicate with this process. 
        # this needs almost each and every settings in the UI....
        self.server = optimizationprocess.start_subprocess(
            lambda pickled_str : self.logging_record_trigger.emit(pickled_str)
            , lambda pickled_str : self.data_update_trigger.emit(pickled_str)
            , mod_name, str(self.module.text()), str(self.function.text())
            , self.objectives.value(), self.variables.value()
            , constraints, int(self.population.text())
            , self.generations.value(), self.elite.value()
            , self.archive.value(), self.mutation.value()
            , str(self.crossover.currentText()), str(self.selection.currentText()))


if __name__ == "__main__": 
    q_app = QtGui.QApplication(sys.argv)
    aw = LibgaGAT()
    aw.show()
    sys.exit(q_app.exec_())
