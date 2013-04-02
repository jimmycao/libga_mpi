import numpy as np
import sys
import glob
import spea2


def recalculate_fitnesses(data, objectives):
    ospace_sqdist = spea2._squared_distances(data[:,-(1 + objectives):-1])
    data[:,-1] = np.asarray([spea2._raw_strength_2(data[:,-(1 + objectives):-1], i)
               + spea2._density_estimator(ospace_sqdist, i)
               for i in range(len(data))])


def merge_to_npz(input_file_pattern, objectives, out_file):
    global_data = None
    for file in glob.glob(input_file_pattern):
        data = np.loadtxt(file, delimiter=' ')
        if global_data == None:
            global_data = data
        else:
            global_data = np.append(global_data, data, axis=0)
    recalculate_fitnesses(global_data, objectives)
    np.savez(out_file, genome=global_data[:, 0:-(1 + objectives)],
             ospace=global_data[:, -(1 + objectives):-1], fitnesses=global_data[:,
             -1])


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_to_npz <input-file-pattern> "
              + "<number-of-objectives> <output-npz-file>")
        sys.exit(1)
    merge_to_npz(input_file_pattern=sys.argv[1], objectives=int(sys.argv[2])
                 , out_file=sys.argv[3]); 
