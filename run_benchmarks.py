import argparse
import glob
import importlib
import os
import datetime
from typing import List

from grammar_generator.ebnf_generator_v5 import generate_ebnf_v5
from main import fuzz_main
from util.util import str_to_bytes

DEFAULT_BENCHMARKS_DIR = "benchmarks"
DEFAULT_PARENT_OUTPUT_DIR = "run_benchmarks_output"
DEFAULT_PARENT_INPUT_DIR = f"{DEFAULT_BENCHMARKS_DIR}/seeds"
DEFAULT_PARENT_GOLDEN_INPUT_DIR = f"{DEFAULT_BENCHMARKS_DIR}/golden_grammar_inputs"

COLOUR_NC='\u001b[0m'
COLOUR_PURPLE='\u001b[0;35m'

class Args():
    def __init__(self,
                 module_to_fuzz: str,
                 output_dir: str,
                 input_dir: str = None,
                 time: int = 10,
                 cumulative: bool = True):
        self.module_to_fuzz = module_to_fuzz
        self.fuzzer = "GRIMOIRE"
        self.output_dir = output_dir
        self.input_dir = input_dir
        self.time = time
        self.cumulative = cumulative

def calculate_precision(grammar, module_to_fuzz, benchmark_output_file = None):
    module_under_test = importlib.import_module(module_to_fuzz)
    ig_positive_examples = grammar.sample_positives(100, 3)
    num_accepted = 0
    num_total = len(ig_positive_examples)
    for example in ig_positive_examples:
        if benchmark_output_file is not None:
            benchmark_output_file.write(f"\n!!! Generated an example from grammar: {example}")
        try:
            module_under_test.test_one_input(str_to_bytes(example))
            num_accepted += 1
        except:
            pass
    precision = num_accepted / num_total if num_total != 0 else 0.0
    return num_accepted, num_total, precision


def calculate_recall(parser, input_dir, benchmark_output_file = None):
    test_input_files = [f for f in glob.glob(f"{input_dir}/*")]
    num_success = 0
    num_total = len(test_input_files)
    for test_input_file in test_input_files:
        with open(test_input_file) as f:
            # f here is contains new string
            inp = f.read()
            if benchmark_output_file is not None:
                benchmark_output_file.write(f"\ninput: {inp}")
            try:
                tree = parser.parse(inp)
                if benchmark_output_file is not None:
                    benchmark_output_file.write(f"\noutput:\n{tree.pretty()}")
                num_success += 1
            except:
                if benchmark_output_file is not None:
                    benchmark_output_file.write(f"\n! failed to parse!")
            f.close()
    recall = num_success / num_total if num_total != 0 else 0.0
    return num_success, num_total, recall


def main(args):
    # setup output directory
    curr_timestamp = datetime.datetime.now().strftime("%m-%d_%H:%M")
    output_dir = f"{args.output_parent_dir}/{curr_timestamp}"
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    benchmarks: List[str] = [os.path.basename(f.strip(".py")) for f in glob.glob(f"{args.benchmarks_dir}/*.py")]
    for benchmark in benchmarks:
        print(f"{COLOUR_PURPLE}Running benchmark {benchmark}...{COLOUR_NC}")
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

            # create output log file
            benchmark_output_file = open(f"{fuzz_output_dir}/benchmark_output.txt", "w")

            # create grammar
            fuzz_output_generalized_inputs = f"{fuzz_output_dir}/generalized_input.json"
            fuzz_output_valid_inputs = f"{fuzz_output_dir}/valid_input.json"
            grammar = generate_ebnf_v5(fuzz_output_generalized_inputs, fuzz_output_valid_inputs)
            benchmark_output_file.write("Grammar:\n")
            benchmark_output_file.write(grammar.pretty_print())
            grammar_parser = grammar.parser()

            # calculate precision and recall
            golden_grammar_input_dir = f"{args.golden_input_parent_dir}/{benchmark}"
            if not os.path.exists(golden_grammar_input_dir):
                golden_grammar_input_dir = input_dir
                benchmark_output_file.write(f"\nGolden grammar inputs for {benchmark} do not exist, using input seeds...")
            precision_accepted, precision_total, precision = calculate_precision(grammar, module_to_fuzz, benchmark_output_file)
            recall_accepted, recall_total, recall = calculate_recall(grammar_parser, golden_grammar_input_dir, benchmark_output_file)

            benchmark_output_file.write(f"\nbenchmark: {benchmark} recall: {recall_accepted}/{recall_total}={recall}, precision: {precision_accepted}/{precision_total}={precision}")
            benchmark_output_file.flush()
            benchmark_output_file.close()
        except Exception as e:
            print(e.args)
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
        "--golden_input_parent_dir",
        type=str,
        help="directory containing directories of golden grammar generated inputs for each benchmark to start coverage-guided fuzzing. Each sub-directory should be the name of a benchmark (eg. calculator) and contain the inputs for that benchmark",
        default=DEFAULT_PARENT_GOLDEN_INPUT_DIR,
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
