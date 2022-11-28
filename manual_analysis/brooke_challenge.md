accepted examples:
```
1. ( RISK /Users/ssun/project/util | LIFE * | MORAL shine:poor | LOVE ++ )
2. ( RISK /Users/ssun/ubc/ | LIFE 2...100 | MORAL poor:shine )
3. ( RISK /Users/ssun/ubc/ | LIFE ...106 | MORAL poor:shine )
4. ( RISK /Users/ssun/ubc/ | LIFE 5... | MORAL poor:shine )
5. ( RISK ../ssun/ubc/ | LIFE 23 | MORAL order:poor | LOVE ---- )
6. ( RISK ../ssun/ubc/ | LIFE piano.rds | MORAL order | LOVE + )
7. ( RISK ../ssun/ubc/ | LIFE piano.rmd )
8. ( LIFE piano.rmd )
9. ( LIFE ../ssun/ubc/viola.rmd |  MORAL order:poor | LOVE -- )
10. ( LIFE /Users/ssun/ubc/viola.rds | LOVE +++++ )
```

not accepted examples:
```
11. (RISK /Users/ssun/project/util|LIFE *|MORAL shine:poor|LOVE ++)
12. ( RISK /Users/ssun/ubc/ test_case | LIFE ... | MORAL poor:shine )
14. ( RISK ../ssun/ubc/ | LIFE 23 | MORAL order:shine | LOVE ---- )
15. ( RISK ../ssun/ubc/ | LIFE 23 | MORAL hello:shine | LOVE ---- )
16. ( RISK ../ssun/ubc/ | MORAL poor:order | LOVE ---- )
17. ( RISK /Users/ssun/project/util | LIFE * | MORAL | LOVE )
18. ( RISK | LIFE piano.rds | MORAL shine:poor | LOVE ---- )
19. ( MORAL poor:shine | RISK /Users/ssun/ubc/ | LIFE piano.rds | LOVE +++ )
```

### notes from the challenge
- every valid input seems to be surrounded by ()
- the content of each input within the () seems to have some structured chunks that look repeated
  - #1 RISK ... LIFE ... 
    - I feel like the capitalized words are important and possibly mark the beginning of a "chunk" in the input??
    - each chunk separated by '|' 
      - BUT there could be just one chunk (#8) or there could be multiple (everything else)
  - there also seems to be a space between everything (parts of an input or a chunk can't be connected)
    - it's true for all accepted examples
    - one of the non-accepted examples #11 shows no space between some places where I'd expect a space based on the accepted examples (eg. between '(' and RISK)
      - idk yet if that's the only thing that causes #11 to fail
      - seems like the most obvious difference compared to other failing examples and compared to accepted examples (but can't really use this fact because it all depends on the examples given :/)
- each chunk has structure `<capitalized word> <string>`
  - there's a failing example (#12, 18) that breaks this; all accepting examples follow this
  - the structure of `string` that comes after `capitalized word` depends on what the `capitalized word` is
    - RISK: `<file path>` 
      - could end in a `/` or not
      - could be absolute or relative
    - LIFE: specifies a number or a range of numbers, or a file or path??
      - based on preexisting knowledge of ??regex??
      - patterns:
        - `*` is everything (wildcard) (#1)
        - `num...` is everything from num onwards (#4)
        - `...num` is everything from start to num (#3)
        - `num...num2` is range of [num, num2] (#2)
        - `num` is only num (#5)
        - `<file>`
        - `<path to file>`
    - MORAL: `word`s separated by `:`
      - word can be `shine`, `poor`, `order`
    - LOVE: one or more `+` or one or more `-`
      - doesn't seem to be restriction on the actual number, other than >=
    - non-accepted examples don't really tell me anything ??
- analysis on failing examples
  11. missing spaces between different parts that make up the structured input
  12. RISK has two strings following it
  13. ???????? (suzie forgot why this was wrong)
  14. ???????????
  15. we don't like hello (not a valid word)
  16. when there's a RISK there always has to be a LIFE??
  17. MORAL and LOVE have no string after it
  18. RISK has no string after it
  19. RISK out of order?
- are different chunks related to each other??
- maybe if a chunk relating to a `capitalized word` exists, then it has to be in the right relative order (relating to other chunks)
- I'm guessing `capitalized word`s can't repeat - no supporting examples (why did I think this as a human!?!?!? bc it's true of all the given accepted examples (although maybe not globally true :thinking:)))
- was gonna say that LIFE is a file only if RISK is a dir, but doesn't seem to always be the case (#8 doesn't have RISK) ALSO why can LIFE be a path?????
- was gonna say maybe RISK is the path (not including a specific file), but when LIFE is a file it's always a specific one :((

- IT'S TIME TO YOLO
- grammar
  - START := '( ' CONTENT ' )'
  - CONTENT := ('RISK' PATH ' | ')? 'LIFE' LIFE (' | ' 'MORAL' MORAL)? (' | ' 'LOVE' LOVE)?
  - PATH := '/'? STR ('/' STR)* '/'?
  - LIFE := '*' | NUM '...' | '...' NUM | PATH? STR '.' STR
  - MORAL := WORD (':' WORD)*
  - LOVE := PLUS | MINUS
  - PLUS := '+' | '+' PLUS
  - MINUS := '-' | '-' MINUS
  - WORD := 'shine' | 'poor' | 'order'
  - STR := any string that only contains letters?
  