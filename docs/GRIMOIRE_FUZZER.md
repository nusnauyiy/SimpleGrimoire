# Grimoire Fuzzer

Run with: `python3 main.py <benchmark.path>.<benchmark> --fuzzer GRIMOIRE --time <seconds> --input_dir <benchmark seed path>/<benchmark>`

-----

SimpleGrimoire is based on the Grimoire fuzzing algorithm, implemented on top of a simple python fuzzer.
- Original Grimoire [paper](https://www.usenix.org/conference/usenixsecurity19/presentation/blazytko) and [repository](https://github.com/RUB-SysSec/grimoire)
- Simple fuzzer base from [UBC CPSC 539L 2022W1](https://www.carolemieux.com/teaching/CPSC539L_2022w1_assign_1.html)

Our goal is to evaluate the potential of Grimoire as a grammar inference tool.

We have implemented two versions:

1. **Naive Grimoire:** an implementation that is mostly faithful to the algorithm described in the original paper. There are a few small additions to facilitate grammar generation for evaluation. The implementation is found in the `simple-algorithm` tag or in the `simple-algo-eval` branch.

2. **Replacement Grimoire:** adds an additional step in Naive Grimoire's generalization phase, where we search for blanks that can be _replaced_ by other content, rather than blanks that can be entirely removed. This implementation is found on the main branch.

Grimoire can roughly be broken down into the following steps:

1. Populate dictionary of values from MUT.
2. Fuzz initial seed inputs.
3. Mutate saved inputs and fuzz them.
4. Save data to output folder.

## 1. Populate dictionary of values from MUT

We traverse the main file of the MUT to collect all constant values (strings and numbers) and store them in a set. These may be used during the mutation step.

For example, if we have the following file as our MUT:
```python
def main():
    for i in range(7):
        print("Hello World!")
```
Our resulting dictionary would be the following set:
```python
{ "7", "Hello World!" }
```

By the end of this step, the fuzzer will have a set of strings extracted from the MUT which can be used during input mutation.

## 2. Fuzz initial seed inputs

The fuzzer keeps a list of saved inputs, which are inputs that have achieved new coverage. To populate the list with initial values, we first fuzz the given input seeds (with no mutations) and save/generalize the ones that achieve new coverage. Generalization is described in a later section below.

The input seed directory is given with the `--input_dir` argument, and contains each input in its own file. 

> Note: If no input seed directory is specified, the fuzzer will use a string of null bytes as the initial input. In this case, evaluation will most likely _not_ work because Lark cannot create a grammar containing null bytes.

Global coverage information is saved in the fuzzer, and coverage that each input has achieved is stored in the saved input object. Coverage is represented by a set of tuples representing transitions between line numbers and files in the MUT (ie. `(start line, end line, file)`).

By the end of this step, the fuzzer will have a list of saved inputs that have achieved new coverage, which it can mutate to generate more inputs.

## 3. Mutate saved inputs and fuzz them

While the time allotted has not been exceeded, the fuzzer will repeatedly choose a saved input and perform the following substeps:
1. Mutate the input.
2. Run the input through the MUT.
3. Save and generalize the input (if applicable).

By the end of this step, the fuzzer will have saved any additional generalized or crashing inputs that it has found.

### 3.1. Mutate the input

There are three types of mutations that are applied to the input. These mutations are applied separately (not cumulatively), and each mutated input is sent to the fuzzer to run through the MUT (step 3.2). Multiple mutated inputs may be generated from a single mutation type. 

#### 1. Input extension 
For inputs with generalizations only; see `fuzzer/GrimoireFuzzer.py:input_extension`.

The input _i_ is extended with a random choice _r_ of:
- Generalized input: a random generalized input is chosen and its blanks are removed. For example, for the random generalized input `["Hello" Blank "!"]`, the string `"Hello!"` will be used.
- Slice: a random string from a random generalized input is chosen. For example, for the random generalized input `["Hello" Blank "!"]`, the string `"!"` may be chosen.
- Token: a string from the dictionary built in [step 1](#1-populate-dictionary-of-values-from-mut).

Mutated inputs _ir_ and _ri_ are sent to the fuzzer.


#### 2. Recursive replacement 
For inputs with generalizations only; see `fuzzer/GrimoireFuzzer.py:recursive_replacement`.

A random gap in the generalization of the input is replaced with a random choice of generalized input, slice, or token (see above). This mutated input is sent to the fuzzer.


#### 3. String replacement
String replacement is done in three steps:
1. All substrings in the input that match strings from the dictionary in [step 1](#1-populate-dictionary-of-values-from-mut) are located and one is chosen randomly, call it _s_. 
2. A random occurrence of _s_ is chosen and replaced with a random string _r_. This mutated input is sent to the fuzzer.
3. All occurrences of _s_ are replaced with _r_, and this mutated input is sent to the fuzzer.


### 3.2. Run the input through the MUT

When a mutated input _m_ is sent to the fuzzer, it is run through the MUT. 

By the end of this step, MUT execution information about _m_ will have been generated. This information includes coverage achieved, time taken, and whether an error occurred. 
 

### 3.3. Save and generalize the input

- If the MUT raises an exception and _m_ achieves more coverage than previous crashing inputs, _m_ is saved as a crashing input.
- If the MUT accepts _m_, _m_ is saved as a valid input (Naive Grimoire only).
- If the MUT accepts _m_ and _m_ achieves more coverage than previous saved inputs, _m_ is [generalized](GENERALIZATION.md) and saved as a saved input.

## 4. Save data to output folder

The generalized inputs are saved as JSON objects to a file called `generalized_input.json`. The data will be in a list, for example:
```json
[
  {
    "data": "21*3",
    "generalized": {
      "input": [
        {
          "removed": "21",
          "type": "REPLACE",
          "replacements": [
            "DIGIT"
          ]
        },
        "*",
        {
          "removed": "3",
          "type": "REPLACE",
          "replacements": [
            "DIGIT"
          ]
        }
      ]
    }
  },
  ...
]
```
The generalized inputs in Replacement Grimoire will have blank information saved as objects containing: 
- removed: the text from the original input that was replaced by the blank
- type: the type of the blank (`DELETE` or `REPLACE`)
- replacements (`REPLACE` only): the [replacement classes](REPLACEMENT_CLASSES.md) that the blank accepts.

The generalized inputs in Naive Grimoire will have blanks represented by an empty object.

This step also saves coverage information, saved inputs, crashing inputs, and valid inputs (for Naive Grimoire). 

By the end of a successful Grimoire run, an output folder should be generated which looks like this:
```
- output
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