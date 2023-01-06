# Simple Grimoire

A version of the Grimoire algorithm implemented on top of a simple python coverage fuzzer.

Run calculator example with:
```
python3 main.py benchmarks.calculator --fuzzer GRIMOIRE --time 10 --input_dir seeds/calculator
````

The source code contains modifications of code found within the original Grimoire repository (https://github.com/RUB-SysSec/grimoire), which is licensed under the [AGPL-3.0 license](LICENSE). 

## things to do
- [ ] finish debugging
  - [ ] quicksort
  - [ ] cgi_decode
  - [ ] mimid
- [ ] implement `havoc_amount`
- [x] finish testing standalone methods
  - [x] `generic_generalized`
  - [x] `merge_adjacent_blanks` in `GeneralizedInput`

## to look into
- [ ] input extension seems to not change the strings very much. this could be because our input string is very short and not many blanks were found for them
- [ ] inputs generated does not seem to make full use of the dictionary supplied. it might also be a chance thing
- [ ] we didn't end up generating many valid inputs. This is likely due to the simple algorithm for finding blanks. we can start look into more complex ones