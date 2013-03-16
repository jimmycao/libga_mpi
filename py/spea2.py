import numpy as np
import time
import heapq
import sys


def _squared_distances(m):
    N = len(m)
    ret = np.zeros((N, N))
    np.fill_diagonal(ret, sys.float_info.max)
    for i in range(N - 1):
        ret[i + 1:, i] = ret[i, i + 1:] = ((m[i] - m[i + 1:])
                ** 2).sum(axis=1)
    return ret

def and_(x, y):
    for (x_i, y_i) in zip(x, y):
        yield x_i and y_i

def not_(x):
    for x_i in x:
        yield not x_i

def _raw_strength_2(ospace, i):
    return sum(1 for x in and_(not_((ospace > ospace[i]).any(axis=1)),
               (ospace < ospace[i]).any(axis=1)) if x)

def _density_estimator(ospace_sqdist, i):
    return 1 / (2 + np.sqrt(ospace_sqdist[i].min()))

def _densest(arr, distances):
    densest_elements = min(((i, j) for i in range(len(arr)) for j in
                           range(i)), key=lambda x: \
                           distances[arr[x[0]], arr[x[1]]])
    return (densest_elements[0] if np.random.random()
            < .5 else densest_elements[1])

def _binary_tournament_selection(selection, fitnesses):
    x = selection[int(np.random.random() * len(selection))]
    y = selection[int(np.random.random() * len(selection))]
    return (x if fitnesses[x] < fitnesses[y] else y)

def _migrate_none(genome, fitnesses): 
    pass

def _merge_none(genome): 
    pass


class Spea2:
    def __init__(self, genome, archive_percentage = .3):
        np.random.seed(int(time.time()))
        self.genome = genome
        assert archive_percentage > 0
        assert archive_percentage <= 1
        self.archive_percentage = archive_percentage

    def start(self, eval_genome_fn, progress_fn,
        xover_fn, is_valid_fn, mutate_fn, max_crossover_attempts = 100
        , migrate_fn = _migrate_none, merge_fn = _merge_none):

        self.generation = 0
        while True:

            # evaluate genome
            self.ospace = eval_genome_fn(self.genome)

            # assign fitness value for each solution candidate
            ospace_sqdist = _squared_distances(self.ospace)
            self.fitnesses = [_raw_strength_2(self.ospace, i)
                + _density_estimator(ospace_sqdist, i)
                for i in range(len(self.genome))]

            # quit? also, report progress to client code
            if not progress_fn():
                return

            # migrate
            migrate_fn(self.genome, self.fitnesses)

            # environmental selection. the size of the selection buffer is
            # determined by self.archive_percentage.
            selection = self.environmental_selection(ospace_sqdist)

            # produce the next generation. this can raise an
            # Exception which signals that no more valid solutions can be found.
            # try checking constraints or increase population.
            next_genome = self.crossover(selection, xover_fn,
                    is_valid_fn, mutate_fn, max_crossover_attempts)

            # merge
            merge_fn(next_genome)

            # swap genomes for the next generation
            (self.genome, next_genome) = (next_genome, self.genome)
            self.generation += 1

    def environmental_selection(self, ospace_sqdist):

        # number of selection elements (equals archive size)
        archive = int(len(self.fitnesses) * self.archive_percentage)

        # all non-dominated solutions
        non_dom = [i for i in range(len(self.fitnesses))
                   if self.fitnesses[i] < 1]
        selection = non_dom[:archive]

        # if we have more non-dominated solutions than slots in the selection buffer
        for d in non_dom[archive:]:
            # apply truncation operator to selection buffer
            # i.e. overwrite densest areas
            selection[_densest(selection, ospace_sqdist)] = d

        # if there are not enough non-dominated solutions then copy the best
        # dominated ones
        if len(selection) < archive:
            dom = (i for i in range(len(self.fitnesses))
                if self.fitnesses[i] >= 1)
            selection.extend(heapq.nsmallest(archive - len(selection),
                             dom, key=lambda i: self.fitnesses[i]))
        return selection

    def crossover(self, selection, xover_fn, is_valid_fn, mutate_fn
        , max_crossover_attempts):

        next_genome = []

        # create the next generation
        for i in range(len(self.genome) - len(selection)):
            attempt = 0
            while True:
                x = _binary_tournament_selection(selection, self.fitnesses)
                y = _binary_tournament_selection(selection, self.fitnesses)
                c = xover_fn(self.genome[x], self.genome[y])
                if is_valid_fn(c):
                    next_genome.append(mutate_fn(c))
                    break
                attempt += 1
                if attempt == max_crossover_attempts:
                    raise Exception('Cannot produce further offspring in '
                                    + 'generation' + str(self.generation)
                                    + '. Try checking '
                                    + 'constraints or increasing population and generations. '
                                    )
        # this generation's selection is next generation's archive
        next_genome.extend([self.genome[i] for i in selection])
        return next_genome
