#!/bin/bash
rm -rf output
if [ -z "$3" ]
  then
    python3 fuzzer.py $2 output --fuzzer $1 --time 10
  else
    python3 fuzzer.py $2 output --fuzzer $1 --time 10 --input_dir $3
fi
