#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import sys


def to_npz(csv_file, objectives, out_file):
    data = np.loadtxt(csv_file, delimiter=' ')
    np.savez(out_file, genome=data[:, 0:-(1 + objectives)],
             ospace=data[:, -(1 + objectives):-1], fitnesses=data[:,
             -1])


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print ('Usage: python to_npz.py <csv-file> <number-of-objectives> "
        + "<output-npz-file>')
        sys.exit(1)
    to_npz(csv_file=sys.argv[1], objectives=int(sys.argv[2]),
           out_file=sys.argv[3])
