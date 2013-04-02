import numpy as np
import sys
import glob
import spea2


def recalculate_fitnesses(ospace, objectives):
    ospace_sqdist = spea2._squared_distances(ospace)
    return np.asarray([spea2._raw_strength_2(ospace, i)
               + spea2._density_estimator(ospace_sqdist, i)
               for i in range(len(ospace))])


def merge_to_npz(input_file_pattern, objectives, out_file):
    global_genome = None
    global_ospace = None
    global_fitnesses = None
    for file in glob.glob(input_file_pattern):
        data = np.load(file)
        if global_genome == None:
            global_genome = data["genome"]
            global_ospace = data["ospace"]
            global_fitnesses = data["fitnesses"]
        else:
            global_genome = np.append(global_genome, data["genome"], axis=0)
            global_ospace = np.append(global_ospace, data["ospace"], axis=0)
            global_fitnesses = np.append(global_fitnesses, data["fitnesses"], axis=0)
    global_fitnesses = recalculate_fitnesses(global_ospace, objectives)
    np.savez(out_file, genome=global_genome, ospace=global_ospace
             , fitnesses=global_fitnesses)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_as_npz <input-file-pattern> "
              + "<number-of-objectives> <output-npz-file>")
        sys.exit(1)
    merge_to_npz(input_file_pattern=sys.argv[1], objectives=int(sys.argv[2])
                 , out_file=sys.argv[3]); 
