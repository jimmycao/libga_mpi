from mpi4py import MPI
import numpy as np


class MigrateRandom: 
    def __init__(self, topo, percentage): 
        self._topo = topo
        self._percentage = percentage
        
    def __call__(self, genome, fitnesses): 
        emmigrants = int(self._percentage * len(genome))
        for i in range(emmigrants):
            x = int(np.random.random() * len(genome))
            y = int(np.random.random() * len(genome))
            emmi = x if fitnesses[x] < fitnesses[y] else y
            for n in self._topo.neighbors: 
                MPI.COMM_WORLD.send(genome[emmi], tag = 0, dest = n)

class MergeRandom: 
    def __init__(self, topo, percentage): 
        self._topo = topo
        self._percentage = percentage
        
    def __call__(self, genome): 
        received = self._receive_all()
        if len(received) > 0:
            max_immigrants = int(len(genome) * self._percentage)
            max_immigrants = len(received) if max_immigrants > len(received) \
                else max_immigrants
            for i in range(max_immigrants):
                genome[int(np.random.random() * len(genome))] = received[i]
        
    def _receive_all(self): 
        received = []
        while MPI.COMM_WORLD.Iprobe(): 
            received.append(MPI.COMM_WORLD.recv(tag = 0))
        return received

class RingTopology: 
    def __init__(self): 
        self.size = MPI.COMM_WORLD.size
        self.rank = MPI.COMM_WORLD.rank
        self.neighbors = [0,0]
        self.neighbors[0] = self.rank + 1 if self.rank < self.size - 1 else 0
        self.neighbors[1] = self.rank - 1 if self.rank > 0 else self.size - 1

class IslandModel: 
    def __init__(self, island, topology = RingTopology
                 , merger = MergeRandom, migrator = MigrateRandom
                 , percentage = 0.1): 
        self.island    = island
        self._topology = topology()
        self._merger   = merger(self._topology, percentage)
        self._migrator = migrator(self._topology, percentage)

    def start(self, eval_genome_fn, progress_fn
              , xover_fn, is_valid_fn, mutate_fn, max_crossover_attempts = 100): 
        return self.island.start(eval_genome_fn, progress_fn
              , xover_fn, is_valid_fn, mutate_fn, max_crossover_attempts 
              , self._migrator, self._merger)
