# End-to-end Run of Grimoire Pipeline

Run with: `./eval.sh <benchmark>`

Grimoire fuzzer is evaluated on a benchmark based on two main metrics: precision and recall.

Evaluation runs in 4 main steps.
1. Run Grimoire fuzzer.
2. Generate EBNF.
3. Create Lark parser from EBNF.
4. Get precision and recall.

## 1. Run Grimoire fuzzer

See [Grimoire fuzzer doc](GRIMOIRE_FUZZER.md) for implementation details.

After successfully running the Grimoire fuzzer on the benchmark (eg. with `./eval.sh <benchmark>`), an output folder will be created with a structure like:
```
- output
  - eval-12345678
    - new_benchmarks.benchmark
      - crashing inputs
        ...
      - html_coverage_report
        ...
      - saved_inputs
        ...
      - .coverage
      - coverage_through_time.csv
      - generalized_input.json
      - GRIMOIRE.log
```


## 2. Generate EBNF.

An EBNF is generated based on the generalized inputs that the fuzzer found.

See [EBNF Generation doc](EBNF_GENERATION.md) for more details.

Example for `calculator` benchmark:
```
start: (digits|start) /\*/x (digits|start) 
      | /\(/x (digits|start) /\)/x
digits: INT
%import common.INT
```

## 3. Create Lark parser from EBNF.

This is done by passing the EBNF grammar as a string to Lark's constructor. 
The result will be a parser that can parse an input using the EBNF.

> Note: We have observed out-of-memory issues at this step, which happens for grammars with rules containing a lot of ORs
(eg. `start: (a|b|c|d|e) /+/x (a|b|c|d|e) /-/x ...`). This seems to be happening because Lark uses non-tail recursive calls to expand each OR into separate rules, resulting in more and more frames on the stack.

## 4. Get precision and recall.

Precision and recall are calculated to evaluate the EBNF grammar.

###  Precision
(# IG inputs accepted by MUT) / (total # IG inputs)

Positive inputs are generated from the inferred EBNF (IG) and fed to the MUT. 
~100 inputs are generated, and the number of inputs that the MUT accepts is counted.

### Recall
(# GG inputs accepted by IG parser) / (total # GG inputs)

Existing inputs generated from the benchmark's golden grammar (or known positive inputs that were not used as seeds in step 1) are fed to the EBNF's parser.
The number of inputs that parse successfully is counted.

# Definitions/Abbreviations

MUT - Module Under Test

IG - Inferred Grammar

GG - Golden Grammar