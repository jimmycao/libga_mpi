import zmq
import subprocess
import multiprocessing
import imp
import os
import numpy as np
import time
import logging
import pickle
import threading
import sys


URI_process_to_host = "tcp://127.0.0.1:5533"
URI_host_to_process = "tcp://127.0.0.1:5534"


# each message is sent via send_multipart( type, content ). if
# there is no content, we send an empty string. 
class MessageType: 
    # logging record from process to UI
    logging_record    = "0"
    # data update (genome, ospace, fitnesses) from process to UI
    data_update       = "1"
    # signals to UI that the optimization process is done
    exit_notification = "2"
    # send a quit request from UI to optimization process
    abort_process     = "3"


# load a module. this is used for modules in a parent path 
# (e.g. sga.py) to avoid any __init__.py and relative import
# trickery. 
def _load_module(path):
    mod_name = os.path.split(path)[1]
    base = os.path.splitext(mod_name)[0]
    return imp.load_source(base, path)
    

# the UI owns a single optimization server once an optimization 
# is started. it will listen in a separate thread. 
class OptimizationServer(threading.Thread):
    def __init__(self, on_logging_record, on_data_update): 
        threading.Thread.__init__(self)
        # save parameters
        self.on_logging_record = on_logging_record
        self.on_data_update = on_data_update

        self.process_is_running = True
        
    def run(self):
        # init context
        self.ctx = zmq.Context()

        # init in and out sockets
        self.out_socket = self.ctx.socket(zmq.PUB)
        self.out_socket.bind(URI_host_to_process)
        self.in_socket = self.ctx.socket(zmq.SUB)
        self.in_socket.setsockopt(zmq.SUBSCRIBE, "")
        self.in_socket.bind(URI_process_to_host)

        while True:
            [t, contents] = self.in_socket.recv_multipart()

            if t == MessageType.exit_notification:
                # stop receiving messages, end thread. no more 
                # abor requests can be sent. 
                self.process_is_running = False
                # clean up zmq
                self.out_socket.close()
                self.in_socket.close()
                self.ctx.term()
                # exit thread
                return 
            if t == MessageType.logging_record:
                # forward logging record to UI
                self.on_logging_record(contents)
                continue
            if t == MessageType.data_update: 
                # forward genome data, ospace and fitnesses to UI
                self.on_data_update(contents)

    def abort_process(self):
        if self.process_is_running:
            # this will "non-violently" end the optimization process 
            # in its next generation
            self.out_socket.send_multipart([MessageType.abort_process, ""])


# send log entries via URI_logger_to_host
class ZMQLogger(logging.Handler):
    def __init__(self, socket): 
        self.out_socket = socket
        logging.Handler.__init__(self)

    def emit(self, record): 
        self.out_socket.send_multipart([MessageType.logging_record
                                        , pickle.dumps(record)])


def _crossover_func(gacommon, name):
    if "SBX" in name:
        return gacommon.sbx_crossover
    if "BLX" in name:
        return gacommon.blxa_crossover


def _selection_func(sga, name):
    if "Binary" in name:
        return sga.BinaryTournamentSelector
    if "Rank" in name:
        return sga.RankSelector
    if "Roulette" in name:
        return sga.RouletteWheelSelector
    if "SUS" in name:
        return sga.SusSelector


# running the optimization algorithm in its own process for safety
class OptimizationClient(multiprocessing.Process):
    def __init__(self, mod_name, mod_path, func_name
                 , objectives, variables, constraints, population
                 , generations, elite, archive, mutation
                 , crossover, selection):
        multiprocessing.Process.__init__(self)

        # save parameters
        self.mod_name    = mod_name
        self.mod_path    = mod_path
        self.func_name   = func_name
        self.objectives  = objectives
        self.variables   = variables
        self.constraints = constraints
        self.population  = population
        self.generations = generations
        self.elite       = elite
        self.archive     = archive
        self.mutation    = mutation
        self.crossover   = crossover
        self.selection   = selection

    # no error handling here, since the module has been "test loaded"
    # in the UI thread before spawning this process. 
    def load_module(self): 
        self.logger.info("Loading custom module with objective function(s)")
        base = os.path.splitext(self.mod_name)[0]
        self.module = imp.load_source(base, self.mod_path)
        self.function = getattr(self.module, self.func_name)

    def run(self):
        # initialize outbound zmq socket
        self.ctx = zmq.Context()
        self.out_socket = self.ctx.socket(zmq.PUB)
        self.out_socket.connect(URI_process_to_host)
 
        np.random.seed(int(time.time()))

        # generate inbound zmq socket
        self.in_socket = self.ctx.socket(zmq.SUB)
        self.in_socket.setsockopt(zmq.SUBSCRIBE, "")
        self.in_socket.connect(URI_host_to_process)

        # set up a file logger
        self.logger = logging.getLogger("optimizationclient")
        self.logger.addHandler(ZMQLogger(self.out_socket))
        self.logger.setLevel(logging.INFO)

        # load the user-supplied objective functions from a python module
        self.load_module()

        # create initial genome
        genome = [self.constraints[:,0] \
               + (self.constraints[:,1] - self.constraints[:,0]) \
               * np.random.random(self.variables) for i in range(self.population)]

        # bind to common module
        self.logger.info("Binding to gacommon.py module")
        gacommon = _load_module("../gacommon.py")

        # create the right algorithm instance. by design all parameters that
        # differ between SGA and SPEA2 are passed to the constructor. 
        # the alg.start() methods of SGA and SPEA2 have identical signatures.
        if self.objectives > 1: 
            self.logger.info("Binding to spea2.py module")
            spea2 = _load_module("../spea2.py")
            self.alg = spea2.Spea2(genome \
                , archive_percentage = self.archive / float(self.population))
        else:
            self.logger.info("Binding to sga.py module")
            sga = _load_module("../sga.py")
            self.alg = sga.SGA(genome \
                , elite_percentage = self.elite / float(self.population) \
                , selector_type = _selection_func(sga, self.selection))

        # finally run the thing
        self.alg.start(
            lambda g : self.function(np.asarray(g))
            , self.on_progress
            , _crossover_func(gacommon, self.crossover)
            , lambda s: gacommon.is_within_constraints(s, self.constraints)
            , lambda s: gacommon.mutate_uniform(s \
                 , self.constraints, prob = self.mutation / 100.0)
        )

        # notify host that we are done
        self.logger.info("Algorithm done.<hr />")
        self.out_socket.send_multipart([MessageType.exit_notification, ""])

        # clean up zmq
        self.out_socket.close()
        self.in_socket.close()
        self.ctx.term()

    def on_progress(self):
        # communicate genome to the host
        # send genome information (dependent on whether we are working
        # with spea2 or with sga).
        genome_info = {"genome":self.alg.genome, "ospace":self.alg.ospace \
                           , "fitnesses":self.alg.fitnesses} \
                if self.objectives > 1 else \
                {"genome":self.alg.genome, "ospace":self.alg.ospace}
        # send info "over the wire"
        self.out_socket.send_multipart([MessageType.data_update \
                , pickle.dumps(genome_info)])        

        # see if there is a request to abort from the UI 
        poller = zmq.Poller()
        poller.register(self.in_socket, zmq.POLLIN)
        if len(poller.poll(0)) > 0:
            # yes, there is a message coming in
            [t, content] = self.in_socket.recv_multipart()
            if t == MessageType.abort_process:
                self.logger.info("Received request to abort")
                return False

        # run until the maximum number of generations have been reached
        return self.alg.generation < self.generations


# start up the server/host, the optimization process and return the 
# server to the UI thread. 
def start_subprocess(on_logging_record, on_data_update
                     , mod_name, mod_path, func_name, objectives
                     , variables, constraints, population, generations
                     , elite, archive, mutation, crossover, selection):
    server = OptimizationServer(on_logging_record, on_data_update)
    client = OptimizationClient(mod_name, mod_path, func_name
           , objectives, variables, constraints, population, generations
           , elite, archive, mutation, crossover, selection)
    server.start()
    client.start()
    return server
