import island_model
import spea2
import gacommon
import test_problems
from mpi4py import MPI
import numpy as np


def main(): 
    population  = 100
    variables   = 5
    generations = 200
    constraints = gacommon.make_constraints_array(variables, -5, +5)
    kursawe_fn  = lambda g: test_problems.kursawe(np.asarray(g))

    genome = [constraints[:,0] + (constraints[:,1]-constraints[:,0])
              * np.random.random(variables) for i in range(population)]

    alg = spea2.Spea2(genome)
    im  = island_model.IslandModel(alg, percentage=.2)

    im.start(
        kursawe_fn, lambda : alg.generation < generations
        , gacommon.blxa_crossover
        , lambda s: gacommon.is_within_constraints(s, constraints)
        , lambda s: gacommon.mutate_uniform(s, constraints, prob=.02)
        )

    np.savez("kursawe_data_" + str(MPI.COMM_WORLD.rank) + ".npz"
             , genome = im.island.genome, ospace = im.island.ospace
             , fitnesses = im.island.fitnesses)

if __name__ == "__main__":
    main()

