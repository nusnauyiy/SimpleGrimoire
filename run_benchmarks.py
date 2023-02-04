import argparse
import glob
import os
import datetime
from typing import List

from main import fuzz_main

DEFAULT_BENCHMARKS_DIR = "benchmarks"
DEFAULT_FUZZER = "GRIMOIRE"
DEFAULT_PARENT_OUTPUT_DIR = "run_benchmarks_output"
DEFAULT_PARENT_INPUT_DIR = f"{DEFAULT_BENCHMARKS_DIR}/seeds"

class Args():
    def __init__(self,
                 module_to_fuzz: str,
                 fuzzer: str,
                 output_dir: str,
                 input_dir: str = None,
                 time: int = 10):
        self.module_to_fuzz = module_to_fuzz
        self.fuzzer = fuzzer
        self.output_dir = output_dir
        self.input_dir = input_dir
        self.time = time

def main(args):
    # setup output directory
    curr_timestamp = datetime.datetime.now().strftime("%m-%d_%H:%M")
    output_dir = f"{args.output_parent_dir}/{curr_timestamp}"
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    benchmarks: List[str] = [os.path.basename(f.strip(".py")) for f in glob.glob(f"{args.benchmarks_dir}/*.py")]
    for benchmark in benchmarks:
        input_dir = f"{args.input_parent_dir}/{benchmark}"
        if not os.path.exists(input_dir):
            input_dir = None
        fuzz_args = Args(
            module_to_fuzz=f"{args.benchmarks_dir}.{benchmark}",
            fuzzer=args.fuzzer,
            output_dir=output_dir,
            input_dir=input_dir,
            time=args.time
        )
        fuzz_output_dir = fuzz_main(fuzz_args)
        print(fuzz_output_dir)
        # run parser generator
        # figure out precision and recall


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--benchmarks_dir",
        type=str,
        help="directory containing benchmark programs to fuzz. Entrypoints must be at the top level of the directory.",
        default=DEFAULT_BENCHMARKS_DIR,
        required=False
    )
    parser.add_argument(
        "--fuzzer",
        type=str,
        choices=["RANDOM", "COVERAGE", "GRIMOIRE"],
        help="Which type of fuzzer to run",
        default=DEFAULT_FUZZER,
        required=False
    )
    parser.add_argument(
        "--output_parent_dir",
        type=str,
        help="parent directory containing output directories from grimoire runs",
        default=DEFAULT_PARENT_OUTPUT_DIR,
        required=False
    )
    parser.add_argument(
        "--input_parent_dir",
        type=str,
        help="directory containing directories of inputs for each benchmark to start coverage-guided fuzzing. Each sub-directory should be the name of a benchmark (eg. calculator) and contain the inputs for that benchmark",
        default=DEFAULT_PARENT_INPUT_DIR,
        required=False
    )
    parser.add_argument(
        "--time",
        type=int,
        help="Search time for which to run fuzzing",
        default=10,
        required=False
    )
    args = parser.parse_args()
    main(args)
