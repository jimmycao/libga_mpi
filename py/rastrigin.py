import island_model
import sga
import gacommon
import test_problems
from mpi4py import MPI
import numpy as np

def main(): 
    population  = 100
    variables   = 5
    generations = 200
    constraints = gacommon.make_constraints_array(variables, -5.12, +5.12)
    rastrigin_fn  = lambda g: test_problems.rastrigin_6(np.asarray(g))

    genome = [constraints[:,0] + (constraints[:,1]-constraints[:,0])
              * np.random.random(variables) for i in range(population)]

    alg = sga.SGA(genome)
    im  = island_model.IslandModel(alg, percentage=.2)

    fittest = im.start(
        rastrigin_fn, lambda : alg.generation < generations
        , gacommon.blxa_crossover
        , lambda s: gacommon.is_within_constraints(s, constraints)
        , lambda s: gacommon.mutate_uniform(s, constraints, prob=.02)
        )

    with open("rastrigin_data_" + str(MPI.COMM_WORLD.rank), "w") as f:
        for v in fittest[0]: 
            f.write(str(v) + " ")        
        f.write(str(fittest[1]))

if __name__ == "__main__":
    main()
