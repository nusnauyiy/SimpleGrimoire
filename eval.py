import argparse
import importlib
import glob

from grammar_generator.ebnf_generator_replacement import generate_ebnf_replacement
from util.util import str_to_bytes

def calculate_precision(grammar, module_to_fuzz, benchmark_output_file = None):
    module_under_test = importlib.import_module(module_to_fuzz)
    num_total = 0
    num_accepted = 0
    for i in range(100):
        ig_positive_examples = grammar.sample_positives(1, 3)
        for example in ig_positive_examples:
            num_total += 1
            if benchmark_output_file is not None:
                print(f"\n!!! Generated an example from grammar: {example}")
                benchmark_output_file.write(f"\n!!! Generated an example from grammar: {example}")
            try:
                module_under_test.test_one_input(str_to_bytes(example))
                benchmark_output_file.write(f"\n== example passed :) ==")
                num_accepted += 1
            except:
                benchmark_output_file.write(f"\n==! example failed :( !==")
    precision = num_accepted / num_total if num_total != 0 else 0.0
    return num_accepted, num_total, precision


def calculate_recall(parser, input_dir, benchmark_output_file = None):
    test_input_files = [f for f in glob.glob(f"{input_dir}/*")]
    num_success = 0
    num_total = len(test_input_files)
    for test_input_file in test_input_files:
        with open(test_input_file) as f:
            # f here contains an input string
            inp = f.read()
            if benchmark_output_file is not None:
                benchmark_output_file.write(f"\ninput: {inp}")
                print(f"\ninput: {inp}")
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

def eval_benchmark(fuzz_output_dir, golden_input_parent_dir, benchmarks_dir, benchmark):
    with open(f"{fuzz_output_dir}/benchmark_output.txt", "w") as benchmark_output_file:
        module_to_fuzz = f"{benchmarks_dir}.{benchmark}"
        fuzz_output_generalized_inputs = f"{fuzz_output_dir}/generalized_input.json"
        grammar = generate_ebnf_replacement(fuzz_output_generalized_inputs)
        benchmark_output_file.write("Grammar:\n")
        print("Grammar:\n")
        benchmark_output_file.write(grammar.lark_str())
        print("getting parser")
        grammar_parser = grammar.parser()
        print("got parser")

        # calculate precision and recall
        golden_grammar_input_dir = f"{golden_input_parent_dir}/{benchmark}"
        precision_accepted, precision_total, precision = calculate_precision(grammar, module_to_fuzz, benchmark_output_file)
        recall_accepted, recall_total, recall = calculate_recall(grammar_parser, golden_grammar_input_dir,
                                                                 benchmark_output_file)
        benchmark_output_file.write(
            f"\nbenchmark: {benchmark} recall: {recall_accepted}/{recall_total}={recall}, precision: {precision_accepted}/{precision_total}={precision}")
        benchmark_output_file.flush()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--benchmarks_dir",
        type=str,
        help="directory containing benchmark programs to fuzz. Entrypoints must be at the top level of the directory.",
        required=False
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        help="name of benchmark",
        required=False
    )
    parser.add_argument(
        "--output_parent_dir",
        type=str,
        help="parent directory containing output directories from grimoire runs",
        required=False
    )
    parser.add_argument(
        "--golden_input_parent_dir",
        type=str,
        help="directory containing directories of golden grammar generated inputs for each benchmark to start coverage-guided fuzzing. Each sub-directory should be the name of a benchmark (eg. calculator) and contain the inputs for that benchmark",
        required=False
    )
    args = parser.parse_args()
    eval_benchmark(args.output_parent_dir, args.golden_input_parent_dir, args.benchmarks_dir, args.benchmark)