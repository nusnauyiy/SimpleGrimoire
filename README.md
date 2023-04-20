# Simple Grimoire

A version of the Grimoire algorithm implemented on top of a [simple python coverage fuzzer](https://www.carolemieux.com/teaching/CPSC539L_2022w1_assign_1.html).

The code contains modifications of code found within the original Grimoire repository (https://github.com/RUB-SysSec/grimoire), which is licensed under the [AGPL-3.0 license](LICENSE).


# Getting Started
## System Requirements
We have successfully run SimpleGrimoire on:
- Windows
- Mac (Intel): 16GB RAM
- Mac (M1)
- Linux: 64 core, 132GB RAM VM


## Setup
Download Python3: https://www.python.org/downloads/
Install the [required python packages](requirements.txt).

## Usage
### Running Grimoire and Evaluation
The `eval.sh` script runs Grimoire on benchmarks and then runs evaluation on the benchmarks.
Run the following on the command line:
```shell
./eval.sh <benchmark>
```
Replace <benchmark> with:
- nothing, to run all single-file benchmarks
- calculator ([source](new_benchmarks/calculator.py))
- cgidecode ([source](new_benchmarks/cgidecode.py))
- mathexpr ([source](new_benchmarks/mathexpr.py))
- microjson ([source](new_benchmarks/microjson.py))
  - Note: with the current implementation, program runs out of memory when creating Lark parser. 
- sexpr ([source](new_benchmarks/sexpr.py))
- urlparse ([source](new_benchmarks/urlparse.py))
- apimd ([source](new_benchmarks/apimd/apimd_parser.py))
  - Multi-file benchmark, with `apimd_parser.py` as the entry point. Original repo: https://github.com/KmolYuan/apimd

### Running Grimoire Fuzzer only
Run the following on command line:
```shell
python3 main.py new_benchmarks.<benchmark> --fuzzer GRIMOIRE --time 10 --input_dir new_benchmarks/unified_train_set/<benchmark>
```
Replace `<benchmark>` with one of the following:
- calculator ([source](new_benchmarks/calculator.py))
- cgidecode ([source](new_benchmarks/cgidecode.py))
- mathexpr ([source](new_benchmarks/mathexpr.py))
- microjson ([source](new_benchmarks/microjson.py))
- sexpr ([source](new_benchmarks/sexpr.py))
- urlparse ([source](new_benchmarks/urlparse.py))

### Running Evaluation only
To run this, you will need to have an existing output folder from running Grimoire on the benchmark.
Run the following on command line:
```shell
python3 eval.py --benchmarks_dir new_benchmarks --benchmark <benchmark> --output_parent_dir output/<benchmark output folder> --golden_input_parent_dir new_benchmarks/unified_test_set
```
Replace `<benchmark>` with a benchmark name, and `<benchmark output folder>` with the folder created from running Grimoire on the benchmark. 

If successful, a `benckmark_output.txt` file will be generated in the same output folder, with precision and recall information at the bottom.

# Documentation

[Grimoire](docs/GRIMOIRE.md): details of implementation of the Grimoire algorithm.

[Evaluation](docs/EVALUATION.md): details of benchmark evaluation.