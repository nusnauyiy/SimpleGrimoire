import os
import sys

def main(args):
    if len(args) < 2:
        print("Usage: python3 make_folder_from_file.py <file with inputs>")
        return
    aggregate_input_file = args[1]
    base_folder = aggregate_input_file.split(".")[0]
    if not os.path.isdir(base_folder):
        os.mkdir(base_folder)
    with open(aggregate_input_file) as f:
        inputs = f.readlines()
        for i in range(len(inputs)):
            inputfile = open(f"{base_folder}/input{i}", "w")
            inputfile.write(inputs[i].rstrip())
            inputfile.close()

if __name__=="__main__":
    main(sys.argv)