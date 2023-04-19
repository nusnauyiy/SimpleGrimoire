# Simple Grimoire

A version of the Grimoire algorithm implemented on top of a simple python coverage fuzzer.

# Getting Started
## System Requirements

## Setup

## Usage
### Running Grimoire Fuzzer

### Evaluation


Run calculator example with:
```
python3 main.py benchmarks.calculator --fuzzer GRIMOIRE --time 10 --input_dir benchmarks/seeds/calculator
```

Check out sample outputs in `sample_output` folder.

The source code contains modifications of code found within the original Grimoire repository (https://github.com/RUB-SysSec/grimoire), which is licensed under the [AGPL-3.0 license](LICENSE).


## WIP

### generating EBNF from grammar mined by GRIMOIRE
Run `cgi_decode` example with sample generalized input in `sample_output/cgi_decode_output` with
```
python3 grammar_generator.py sample_output/output_cgi_decode/generalized_input.json
```

### generating a parser from grammar mined by GRIMOIRE
Create file with example to parse. 
Run `cgi_decode` example with sample generalized input in `sample_output/cgi_decode_output` with
```
python3 parser_generator.py sample_output/output_cgi_decode/generalized_input.json <file path to example to parse>
```
