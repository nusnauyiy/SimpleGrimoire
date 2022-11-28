### Accepted inputs
```
1. ~(o u o)~
2. (  .  v .)__(. v  .  )
3. ["  - w-]\('u' )
4. ,(=-=),
5. ( . . ")
6. -{ ;v; }--{ ;_; }--{ ;n; }-
7. \(o u ~)/
8. -(---)/~['w;    ]/
9. _[                  - -                  ]_
10. [.']['.]
11. _(" o-)/
```

### Rejected inputs
```
12. \(ono(/
13. (' u )
14. -(..))-
15. [uuu]
16. \{{ 'u' }}/
17. [._.] [._.] [._.]
18. -(  o u )o-
19. _( "'.'") /
20. }:-;)'=(],,u-n  " ;(({])")'
```


### notes from the challenge
- first observations on the valid input
  - for every parenthesis there are, there is a closing one; as well as the square brackets and curly brackets
  - also there seems to be some symmetry going on
    - like for the 9th observation the spaces are the same?
    - also the same for 1, 2, 10; the entire input is a mirror
    - but that's not always the case...
- first observations on the invalid inputs
  - the brackets are not matching
  - surprisingly 19 is not valid because it looks very symmetrical and also 17, 16
  - seems like you're not supposed to have nested brackets, maybe that's why 16 is invalid; so all the brackets are parallel??
    - meaning you're supposed to only use 1 at a time?
  - actually maybe 17 is invalid because there's a space between each of the faces? none of the valid ones with multiple faces have a space between
    - for example look at 2, 6, 3, etc.
- okay moving onto trying to build a grammar ig
  - SO
    - start with a pair of brackets : (), {}, []
      - was gonna say all of them have a pair of eyes- but #10 doesn't!?
      - they either have two eyes and a mouth, one eye and mouth (10), two eyes with no mouth, and sometimes have a sweat " (3, 5) to either the left and right of the eye+mouth but not both (19)
      - the face can be arbitrarily wide so the positioning (spacing) between the eyes and the mouth doesn't really matter?
    - to sum, the eyes consists of any of the following: these can be terminals for the eyes ig
      - .
      - `-`
      - o
      - '
      - ~
      - ;
      - =
      - ~~(space)~~
    - to sum, the mouth are any of the following
      - u
      - v
      - w
      - n
      - .
      - o
      - (space) which could eliminate the previous thought that you could not have a mouth - so you always have a mouth
        - but seems like you would at least always have at least an eye
      - `-`
    - now let's look at the stuff outside the face
      - it seems like you can have either one or two hands! to either side of the face
      - a hand can be one of these
        - ~
        - _
        - ,
        - /
        - \
    - aside: wait is #10 actually a face? it has a cheek, two eyes, and a nose
      - but judging from Brooke's reaction
        - it's not true
    - okay just gonna double check the invalid examples to make sure everything here is valid
      1. no bracket pair
      1. huh
         1maybe you can't have space as eyes after all??? then why is 10 true i'm confused
      1. no bracket pair
      2. eye symbol incorrect
      3. double brackets
      4. hand symbol invalid
      5. eye outside of face
      6. sweat can only occur on one side
      7. jumboed mess idk what this is
    - i'm mostly confused about why #10 is valid hmmm
      - i guess i don't have to get the whole grammar correct so i'll just go for it
- grammar making time
  - S = (space) | (space)S
  - EYE = . | - | o | ' | ~ | ; | =  and not space i guess
  - MOUTH = u | v | w | n | , | o | - | (space)
  - HAND = ~ | _ | , | / | \ | epsilon
  - CONTENT = S+EYE+S+MOUTH+S+EYE | S+EYE+MOUTH+S | S+MOUTH+EYE+S
    - now I am thinking that number 13 is invalid because it uses (space) for eye but that's not allowed?
    - here + means concating the symbols
    - observe for 10 and 11, for the remaining mouth and eye there are no space, and hence case 2
  - SWEAT = "+CONTENT | CONTENT+"
  - FACE = (SWEAT) | {SWEAT} | [SWEAT]
  - PEOPLE = HAND+FACE+HAND | PEOPLE+PEOPLE
- yayy!!!!


### observations from watching suzie work ;))
interesting observations that might be useful for generalizing grammars
- looking for patterns (and including supporting examples)
    - symmetry in valid inputs
    - recognized concept of a "face", and the constituent components
- analysing invalid inputs that seem to follow the pattern
    - incorrect assumptions or special cases
    - ambiguous grammars
    
- once a pattern is recognized, terminals are chosen depending on which characters satisfy the pattern from the valid examples    

analysis steps go like this:
1. make an initial assumption based on some recurring pattern
2. cross-check with all examples to see if it's a valid rule
3. once rule is verified, find relevant terminals relating to the pattern

notes as challenger:
- in challenge, examples do not cover the whole range of combinations possible
- maybe grimoire would only be able to detect 1 "layer" of grammar since the entire input would fail if grammar doesn't have a recursive structure
    - maybe would struggle with individual components (eg. eyes, mouth)??; would only be able to replace entire faces, but maybe not individual eyes etc

ideas:
- get proportions of occurrence of alphanumeric characters and non-alphanumeric characters in each of generalized tokens and removed tokens
    - maybe can make some generalizations on the generalized inputs based on %
- grammar rules would be very flattened (if multiple ways of writing the grammar exist)
    

