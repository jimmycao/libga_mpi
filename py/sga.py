import numpy as np
import time
import heapq
import sys
from operator import itemgetter


def _random_array_value(arr):
    return arr[np.random.randint(0, len(arr))]

def _random_bucket_2(sequence, r):
    return np.searchsorted(sequence, r) - 1

class SelectorBase(object):
    def __init__(self, candidates, fitnesses):
        pass
    def __call__(self):
        pass

class RouletteWheelSelector(SelectorBase):
    def __init__(self, fitnesses):
        self.likelihoods = np.cumsum(1 / fitnesses / (1
                / fitnesses).sum())

    def __call__(self):
        r = np.random.random()
        return _random_bucket_2(self.likelihoods, r)

class SusSelector(RouletteWheelSelector):
    def __init__(self, fitnesses):
        RouletteWheelSelector.__init__(self, fitnesses)

    def __call__(self):
        r1 = np.random.random()
        r2 = r1 + (1 - r1) * np.random.random()
        return _random_bucket_2(self.likelihoods, r2)

class RankSelector(SelectorBase):
    def __init__(self, fitnesses):
        new_fitnesses = zip(*sorted(enumerate(fitnesses),
                            key=itemgetter(1)))[0]
        self.roulette_wheel_selector = \
            RouletteWheelSelector(np.asarray(new_fitnesses) + 1.0)

    def __call__(self):
        return self.roulette_wheel_selector()

class BinaryTournamentSelector(SelectorBase):
    def __init__(self, fitnesses):
        self.fitnesses = fitnesses

    def __call__(self):
        x = np.random.random(len(self.fitnesses))
        y = np.random.random(len(self.fitnesses))
        return (x if self.fitnesses[x] < self.fitnesses[y] else y)

def _migrate_none(genome, fitnesses): 
    pass

def _merge_none(genome): 
    pass

class SGA:
    def __init__(self, genome, elite_percentage = .3, selector_type = RankSelector):
        np.random.seed(int(time.time()))
        assert elite_percentage >= 0
        assert elite_percentage <= 1
        self.genome = genome
        self._selector_type = selector_type
        self._elite_percentage = elite_percentage

    def start(self, eval_genome_fn, progress_fn,
        xover_fn, is_valid_fn,  mutate_fn, max_crossover_attempts = 100
        , migrate_fn = _migrate_none, merge_fn = _merge_none): 

        self.generation = 0

        while True:

            # evaluate genome
            self.ospace = eval_genome_fn(self.genome)

            # quit? also, report progress to client code
            if not progress_fn():
                return self.fittest()

            # migrate
            migrate_fn(self.genome, self.ospace)

            # produce the next generation. this can raise an
            # Exception which signals that no more valid solutions can be found.
            # try checking constraints or increase population.
            next_genome = self.crossover(self._selector_type(self.ospace),
                xover_fn, is_valid_fn, mutate_fn, max_crossover_attempts)

            # merge
            merge_fn(next_genome)

            # swap genomes for the next generation
            (self.genome, next_genome) = (next_genome, self.genome)
            self.generation += 1

        return self.fittest()

    def crossover(self, selector, xover_fn, is_valid_fn,
        mutate_fn, max_crossover_attempts):

        next_genome = []
        elite = int(len(self.genome) * self._elite_percentage)

        # create the next generation
        for i in range(len(self.genome) - elite):
            attempt = 0
            while True:
                x = selector()
                y = selector()
                c = xover_fn(self.genome[x], self.genome[y])
                if is_valid_fn(c):
                    next_genome.append(mutate_fn(c))
                    break
                attempt += 1
                if attempt == max_crossover_attempts:
                    raise Exception('Cannot produce further offspring in '
                                    + 'generation'
                                    + str(self.generation)
                                    + '. Try checking '
                                    + 'constraints or increasing population and generations. '
                                    )

        # make the elite stay for the next generation
        next_genome.extend(zip(*heapq.nsmallest(elite, zip(self.genome,
                           self.ospace), key=itemgetter(1)))[0])
        return next_genome

    def fittest(self):
        best = min(enumerate(self.ospace), key=itemgetter(1))[0]
        return (self.genome[best], self.ospace[best])


