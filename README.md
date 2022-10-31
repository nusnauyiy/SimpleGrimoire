hihihihi

yayyyyyyy

hello~~~~~~~~

Run mimid example with:
```
python3 main.py benchmarks.mimid output --fuzzer GRIMOIRE --time 10 --input_dir seeds/mimid
````

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