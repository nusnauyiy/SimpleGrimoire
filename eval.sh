#!/bin/bash
timestamp=$(date +%s)
if [ -n "$1" ]
then
  python3 main.py new_benchmarks.$1 --fuzzer GRIMOIRE --time 10 --input_dir new_benchmarks/unified_train_set/$1 --output_dir output/eval-$timestamp
  python3 eval.py --benchmarks_dir new_benchmarks --benchmark $1 --output_parent_dir output/eval-$timestamp/new_benchmarks.$1 --golden_input_parent_dir new_benchmarks/unified_test_set
  exit 0
fi

for benchmark in calculator cgidecode mathexpr sexpr urlparse microjson
do
  echo $benchmark
  python3 main.py new_benchmarks.$benchmark --fuzzer GRIMOIRE --time 10 --input_dir new_benchmarks/unified_train_set/$benchmark --output_dir output/eval-$timestamp
  python3 eval.py --benchmarks_dir new_benchmarks --benchmark $benchmark --output_parent_dir output/eval-$timestamp/new_benchmarks.$benchmark --golden_input_parent_dir new_benchmarks/unified_test_set
done
