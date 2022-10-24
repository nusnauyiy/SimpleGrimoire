import argparse
import coverage
import importlib
import inspect
import os

from fuzzer.CoverageGuidedFuzzer import CoverageGuidedFuzzer
from fuzzer.RandomFuzzer import RandomFuzzer
from fuzzer.GrimoireFuzzerr import GrimoireFuzzer
from util.util import log


def _read_input_dir(input_dir):
    """
    Read the data from the files in `input_dir` into an input set to seed coverage-guided fuzzing.
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"{input_dir} does not exist, cannot retrieve seed inputs")
    inputs = set()
    for filename in os.listdir(input_dir):
        full_name = os.path.join(input_dir, filename)
        if os.path.isfile(full_name):
            input_data = open(full_name, "rb").read()
            inputs.add(input_data)
    if len(inputs) == 0:
        raise ValueError(f"{input_dir} does not contain any readable files.")
    return inputs


def fuzz_main(args):
    """
    Sets up output/input directories, and delegates the fuzzing to a Fuzzer object.
    """
    log("Setting up fuzzing session...")
    # Set up output directory
    output_dir_name = args.output_dir
    if os.path.isdir(output_dir_name):
        raise ValueError(f"{output_dir_name} already exists, not overwriting")
    os.mkdir(output_dir_name)

    # Get the module under test
    module_under_test = importlib.import_module(args.module_to_fuzz)
    if not hasattr(module_under_test, "test_one_input") or not callable(
            module_under_test.test_one_input
    ):
        raise ValueError(
            f"No function named test_one_input in module {module_under_test}"
        )
    test_file_name = inspect.getfile(module_under_test)
    cov = coverage.Coverage(
        branch=True, data_file=os.path.join(output_dir_name, ".coverage")
    )

    if args.fuzzer == "RANDOM":
        fuzzer = RandomFuzzer(module_under_test, test_file_name, cov, args.output_dir)
    elif args.fuzzer == "COVERAGE":
        if args.input_dir is not None:
            inputs = _read_input_dir(args.input_dir)
        else:
            inputs = None
        fuzzer = CoverageGuidedFuzzer(
            module_under_test, test_file_name, cov, args.output_dir, inputs
        )
    elif args.fuzzer == "GRIMOIRE":

        if args.input_dir is not None:
            inputs = _read_input_dir(args.input_dir)
        else:
            inputs = None
        fuzzer = GrimoireFuzzer(
            module_under_test, test_file_name, cov, args.output_dir, inputs
        )

    # Run all the fuzzing
    log("Starting fuzzing session.")
    fuzzer.fuzz(args.time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        add_help=False,
        description="Fuzz the `test_one_input` function in a given module. Tracks coverage of the given module achieved by fuzzing.",
    )
    parser.add_argument(
        "module_to_fuzz",
        type=str,
        help="the module to fuzz. Must contain function named `test_one_input`. Base directory for module must be on your PYTHONPATH",
    )
    parser.add_argument(
        "output_dir", type=str, help="directory in which to put output results"
    )

    parser.add_argument(
        "--fuzzer",
        type=str,
        choices=["RANDOM", "COVERAGE", "GRIMOIRE"],
        help="Which type of fuzzer to run",
        default="RANDOM",
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="directory containing inputs to start coverage-guided fuzzing",
    )
    parser.add_argument(
        "--time", type=int, default=60, help="Search time for which to run fuzzing"
    )
    args = parser.parse_args()
    fuzz_main(args)
