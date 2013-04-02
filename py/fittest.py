import sys
import glob
import numpy as np


def fittest(input_file_pattern): 
    min_fitness_vec = None
    for file in glob.glob(input_file_pattern): 
        data = np.loadtxt(file)
        if min_fitness_vec == None:
            min_fitness_vec = data
        else:
            if data[-1] < min_fitness_vec[-1]: 
                min_fitness_vec = data
    return (min_fitness_vec[:-1], min_fitness_vec[-1])


if __name__ == "__main__": 
    if len(sys.argv) != 2: 
        print("Usage: python fittest.py <input-file-pattern>")
        sys.exit(1)
    f = fittest(sys.argv[1])
    for v in f[0]: 
        print str(v), 
    print(" fit: " + str(f[1]))
