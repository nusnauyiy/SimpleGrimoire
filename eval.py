import argparse

from grammar_generator.ebnf_generator_replacement import generate_ebnf_replacement
from run_benchmarks import calculate_precision, calculate_recall


def eval_benchmark(fuzz_output_dir, golden_input_parent_dir, benchmarks_dir, benchmark):
    with open(f"{fuzz_output_dir}/benchmark_output.txt", "w") as benchmark_output_file:
        module_to_fuzz = f"{benchmarks_dir}.{benchmark}"
        fuzz_output_generalized_inputs = f"{fuzz_output_dir}/generalized_input.json"
        grammar = generate_ebnf_replacement(fuzz_output_generalized_inputs)
        benchmark_output_file.write("Grammar:\n")
        benchmark_output_file.write(grammar.lark_str())
        grammar_parser = grammar.parser()

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