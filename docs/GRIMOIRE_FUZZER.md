# Grimoire Fuzzer

Run with: `python3 main.py <benchmark.path>.<benchmark> --fuzzer GRIMOIRE --time <seconds> --input_dir <benchmark seed path>/<benchmark>`

-----

SimpleGrimoire is based on the Grimoire fuzzing algorithm, implemented on top of a simple python fuzzer.
- Original Grimoire [paper](https://www.usenix.org/conference/usenixsecurity19/presentation/blazytko) and [repository](https://github.com/RUB-SysSec/grimoire)
- Simple fuzzer base from [UBC CPSC 539L 2022W1](https://www.carolemieux.com/teaching/CPSC539L_2022w1_assign_1.html)

Our goal is to evaluate the potential of Grimoire as a grammar inference tool.

We have implemented two versions:

1. **Naive Grimoire:** an implementation that is mostly faithful to the algorithm described in the original paper. There are a few small additions to facilitate grammar generation for evaluation.

2. **Replacement Grimoire:** adds an additional step in Naive Grimoire's generalization phase, where we search for blanks that can be _replaced_ by other content, rather than blanks that can be entirely removed.

SimpleGrimoire can roughly be broken down into the following steps:

1. Populate dictionary of values from MUT.
2. Fuzz initial seed inputs.
3. Mutate saved inputs and fuzz them.
4. Save data to output folder.

## 1. Populate dictionary of values from MUT.

We traverse the main file of the MUT to collect all constant values (strings and numbers) and store them in a set. These may be used during the mutation step.

For example, if we have the following file:
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

## 2. Fuzz initial seed inputs.

The fuzzer keeps a list of saved inputs, which are inputs that have achieved new coverage. To populate the list with initial values, we first fuzz the given input seeds (with no mutations) and save/generalize the ones that achieve new coverage. Generalization is described in a later section below.

The input seed directory is given with the `--input_dir` argument, and contains each input in its own file. 

> Note: If no input seed directory is specified, the fuzzer will use a string of null bytes as the initial input. In this case, evaluation will most likely _not_ work because Lark cannot create a grammar containing null bytes.

Global coverage information is saved in the fuzzer, and coverage that each input has achieved is stored in the saved input object. Coverage is represented by a set of tuples representing transitions between line numbers and files in the MUT (ie. `(start line, end line, file)`).

By the end of this step, the fuzzer will have a list of saved inputs that have achieved new coverage, which it can mutate to generate more inputs.

## 3. Mutate saved inputs and fuzz them.

While the time allotted has not been exceeded, the fuzzer will repeatedly choose a saved input and perform the following substeps:
1. Mutate the input.
2. Run the input through the MUT.
3. Save and generalize the input (if applicable).

By the end of this step, the fuzzer will have saved any additional generalized or crashing inputs that it has found.

### 3.1. Mutate the input.

TODO

### 3.2. Run the input through the MUT.

TODO

### 3.3. Save and generalize the input (if applicable).

TODO

## 4. Save data to output folder.

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

The generalized inputs in Naive Grimoire will have blanks represented by an empty object. Naive Grimoire also saves all valid inputs (all inputs that were accepted by the MUT, regardless of coverage information) to use during [EBNF generation](EBNF_GENERATION.md).


