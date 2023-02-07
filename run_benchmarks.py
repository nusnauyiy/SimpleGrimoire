import argparse
import glob
import importlib
import os
import datetime
from typing import List

from grammar_generator import parser_generator
from main import fuzz_main
from util.util import str_to_bytes

DEFAULT_BENCHMARKS_DIR = "benchmarks"
DEFAULT_PARENT_OUTPUT_DIR = "run_benchmarks_output"
DEFAULT_PARENT_INPUT_DIR = f"{DEFAULT_BENCHMARKS_DIR}/seeds"

class Args():
    def __init__(self,
                 module_to_fuzz: str,
                 output_dir: str,
                 input_dir: str = None,
                 time: int = 10):
        self.module_to_fuzz = module_to_fuzz
        self.fuzzer = "GRIMOIRE"
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
        try:
            # run the benchmark on the fuzzer; TODO: error handling (when fuzzer returns no result)
            input_dir = f"{args.input_parent_dir}/{benchmark}"
            if not os.path.exists(input_dir):
                input_dir = None
            module_to_fuzz = f"{args.benchmarks_dir}.{benchmark}"
            fuzz_args = Args(
                module_to_fuzz=module_to_fuzz,
                output_dir=output_dir,
                input_dir=input_dir,
                time=args.time
            )
            fuzz_output_dir = fuzz_main(fuzz_args)


            # run parser generator on the result
            # TODO: make less ugly
            num_success, num_total, grammar = parser_generator.main([
                "",
                f"{fuzz_output_dir}/generalized_input.json",
                f"{fuzz_output_dir}/valid_input.json",
                input_dir
            ])

            # calculate precision
            recall = num_success / num_total # feed true valid inputs into generated parser

            # calculate recall - feed parser generated inputs into MUT
            module_under_test = importlib.import_module(module_to_fuzz)
            ig_positive_examples = grammar.sample_positives(10, 3)
            num_accepted = 0
            for example in ig_positive_examples:
                print(f"!!! Generated an example from grammar: {example}")
                try:
                    module_under_test.test_one_input(str_to_bytes(example))
                    num_accepted += 1
                except:
                    pass
            precision = num_accepted / len(ig_positive_examples)
            print(f"benchmark: {benchmark} recall: {recall}, precision: {precision}")
        except:
            print(f"Error fuzzing benchmark {benchmark}, aborting...")
            continue


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
