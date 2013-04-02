# -*- coding: utf-8 -*-
import numpy as np
import sys


def front(in_file, out_file):
    data = np.load(in_file)
    genome = data["genome"]
    ospace = data["ospace"]
    fitnesses = data["fitnesses"]
    selected = fitnesses < 1
    np.savez(out_file, genome=genome[selected], ospace=ospace[selected]
             , fitnesses=fitnesses[selected])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python front.py <source-npz-file> <dest-npz-file>")
        sys.exit(1)
    front(in_file=sys.argv[1], out_file=sys.argv[2])
