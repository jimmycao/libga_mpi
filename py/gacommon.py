import numpy as np


def make_constraints_array(variables, cnst_min, cnst_max):
    return np.asarray([cnst_min, cnst_max]
                      * variables).reshape((variables, 2))

def is_within_constraints(solution, constraints):
    return np.all(solution >= constraints[:, 0]) and np.all(solution
            <= constraints[:, 1])

def sbx_crossover(x, y, mu=2):
    R = np.random.random()
    b = (pow(2 * R, 1 / (mu + 1)) if R <= .5 else pow(.5 / (1 - R), 1
         / (mu + 1)))
    if np.random.random() <= .5:
        b = -b
    return .5 * ((1 + b) * x + (1 - b) * y)

def blxa_crossover(x, y, a=.5):
    low = np.minimum(x, y)
    high = np.maximum(x, y)
    I = (high - low) * a
    R = np.random.random(len(x))
    return 2 * I * R - I + high * R - low * R + low

def mutate_uniform(x, constraints, prob=.03):
    for i in range(len(x)):
        if np.random.random() < prob:
            x[i] = constraints[i, 0] + (constraints[i, 1]
                    - constraints[i, 0]) * np.random.random()
    return x
