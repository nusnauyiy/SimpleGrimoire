# Evaluation Examples
### already imported
1. face-grammar
    ```
    python3 search.py external ./eval-examples/face-grammar/face-grammar.sh eval-examples/face-grammar/train_set eval-examples/face-grammar/face-grammar.log

    python3 eval.py external -n 50 ./eval-examples/face-grammar/face-grammar.sh eval-examples/face-grammar/test_set eval-examples/face-grammar/face-grammar.log
    ```
1. calculator
    ```
    python3 search.py external ./eval-examples/calculator/calculator.sh eval-examples/calculator/train_set eval-examples/calculator/calculator.log

    python3 eval.py external -n 50 ./eval-examples/calculator/calculator.sh eval-examples/calculator/test_set eval-examples/calculator/calculator.log
    ```
1. cgidecode
    ```
    python3 search.py external ./eval-examples/cgidecode/cgidecode.sh eval-examples/cgidecode/train_set eval-examples/cgidecode/cgidecode.log

    python3 eval.py external -n 50 ./eval-examples/cgidecode/cgidecode.sh eval-examples/cgidecode/test_set eval-examples/cgidecode/cgidecode.log
    ```
### adding and running a new python example
1. import the python source code (`[example-file].py`) to `eval-examples/[example-dir]`, along with a directory `test-set` and `train-set`, each with appropriate example `.ex` files.
1. ensure the source code is modified such that it exits with code 0 when an example is valid, and 1 when the example is invalid.
1. create a wrapper `[example-file].sh` file as follows
    ```
    #!/bin/sh

    python eval-examples/[example-dir]/[example-file].py $1
    ```
1. from the root directory, run
`python3 search.py external ./eval-examples/[example-dir]/[example-file].sh eval-examples/[example-dir]]/train_set [example-file]].log`

1. Once a `.grammardict` file is created from the command above, run
`python3 eval.py external -n 100 ./eval-examples/[example-dir]/[example-file].sh eval-examples/[example-dir]/test_set [example-dir].log` to evaluate the grammar mined
