# Simple Grimoire

A version of the Grimoire algorithm implemented on top of a simple python coverage fuzzer.

Run calculator example with:
```
python3 main.py benchmarks.calculator --fuzzer GRIMOIRE --time 10 --input_dir seeds/calculator
```

The source code contains modifications of code found within the original Grimoire repository (https://github.com/RUB-SysSec/grimoire), which is licensed under the [AGPL-3.0 license](LICENSE).

[//]: # (## to look into)
[//]: # (- [ ] input extension seems to not change the strings very much. this could be because our input string is very short and not many blanks were found for them)