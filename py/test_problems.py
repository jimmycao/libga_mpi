import numpy as np


# multi-objective test problem
# typically 5 variables in [-5, +5]
def kursawe(genome):
    ret = np.zeros((len(genome), 2))
    ret[:,0] = -10 * np.exp(-.2 * np.sqrt(genome[:,:-1]**2 + genome[:,1:]**2)).sum(axis=1)
    ret[:,1] = (np.abs(genome)**.8 + 5*np.sin(genome)**3).sum(axis=1)
    return ret

# single-objective test function (search within [-5.12,+5.12])
def de_jong_1(genome):
    return (genome * genome).sum(axis=1)

# single-objective test function (search within [-2.048,+2.048])
def de_jong_2(genome):
    return (100 * (genome[:, 1:] - genome[:, :-1]) ** 2 + 1 - genome
            ^ 2).sum(axis=1)

# single-objective test function (search within [-5.12,+5.12])
def rastrigin_6(genome):
    return 10 * genome.shape[1] + (genome ** 2 - 10 
        * np.cos(2 * np.pi * genome)).sum(axis=1)

# multi-objective test problem
# MOP5 by Viennet. two variables in [-30, +30]
def MOP5(genome): 
    ret = np.zeros((len(genome), 3))
    ret[:,0] = 0.5 * (genome[:,0]**2 + genome[:,1]**2)          \
       + np.sin(genome[:,0]**2 + genome[:,1]**2)
    ret[:,1] = ((3*genome[:,0] - 2*genome[:,1] + 4)**2) / 8     \
       + ((genome[:,0] - genome[:,1] + 1)**2) / 27 + 15
    ret[:,2] = 1 / (genome[:,0]**2 + genome[:,1]**2 + 1)        \
       - 1.1 * np.exp(-genome[:,0]**2 - genome[:,1]**2)
    return ret
