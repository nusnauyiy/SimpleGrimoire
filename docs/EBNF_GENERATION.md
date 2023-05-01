# EBNF Generation

Code in `grammar_generator` folder.

-----

# Overview
Over the course of SimpleGrimoire's development, we experimented with different methods of EBNF generation. They are listed below; some work better than others. 

EBNF v5 is the grammar generation method for Naive Grimoire. EBNF replacement is the grammar generation method for Replacement Grimoire.

# Versions

## EBNF v1

Code: `grammar_generator/ebnf_generator.py:generate_ebnf`

Input: `generalized_input.json` file.

This grammar has two non-terminals: `start` and `terminal`. It is not recursive.
- Each subrule in `start` is created from the generalized inputs, replacing all blanks with `terminal`.
- `terminal` is one or more letters/digits. 

Example:
```
start: terminal "3+" terminal "2" | terminal
terminal: (DIGIT | LETTER)+
```

Since terminal matches one or more letters/digits, it runs into parsing ambiguity issues. For example, with the grammar above and the input "23+22", the parser will run into an error where it tries the first subrule of `start` and matches "23" as the first `terminal` expansion. From here, it will be unable to match the "3+" string in the rule and conclude that the input does not match that subrule. Similarly, it will try other subrules and fail on those, and ultimately fail to parse the input.

Note: originally, `terminal` expanded to the regex `/.+/`. We ran into the problem above and tried to fix it by using `(DIGIT | LETTER)+` instead, but the grammar still ran into the same issue.


## EBNF v2

Code: `grammar_generator/ebnf_generator.py:generate_ebnf_v2`

Input: `generalized_input.json` file.

This grammar tries to address the parsing error seen in EBNF v1 by converting entire subrules into regex. It is not recursive.

Example:
```
start: /.+3\+2/ | /.+/
```

A drawback to this method is that it is difficult to convert to a CFG, or to glean any proper parse tree structure from it. 

## EBNF v3

Code: `grammar_generator/ebnf_generator.py:generate_ebnf_v3`

Input: `generalized_input.json` file.

This grammar tries to address the parsing error seen in EBNF v1 by using only the substrings which were replaced by blanks in the generalized inputs. Also, terminals are all converted to regex since using strings would not work if we wanted to match double quotes (`"`). It is not recursive.

Example:
```
start: terminal /3\+/ terminal /2/ | /.+/
terminal: /substring1/ | /substring2/ | ...
```

A drawback to this method is that it generalizes extremely poorly, since `terminal` contains a very limited set of strings.

## EBNF v4

Code: `grammar_generator/ebnf_generator.py:generate_ebnf_v4`

Input: `generalized_input.json` file.

This grammar builds on EBNF v3 by adding a recursive rule `term`, which can either expand back to `start` or expand to `terminal`. This recursion is naive, since it is the same for all grammars and does not take any possible recursive structures of seen inputs into consideration.  

Example:
```
start: term /3\+/ term /2/ | /.+/
term: start | terminal
terminal: /substring1/ | /substring2/ | ...
```

A drawback to this method is that it still generalizes poorly due to the limited set of strings in `terminal`.

## EBNF v5

Code: `grammar_generator/ebnf_generator_v5.py`

Input: `generalized_input.json` and `valid_input.json` files.

This grammar tries to address the generalization issues seen in EBNF v3/v4 by taking substrings from all valid inputs, not just those that have been generalized.

This is accomplished in the following steps:
1. Convert all generalized inputs into regexes, replacing blanks with `(.+)`.
2. Pattern match each valid input with each of the regexes.
3. If any of the regexes match, collect the substrings that matched the groups `(.+)` in the regex.

Example:
```
start: term /3\+/ term /2/ | /.+/
term: start | terminal
terminal: /substring1/ | /substring2/ | ...
```

A drawback to this method is that it is extremely messy, and although it generalizes better than previous methods, it still doesn't generalize super well.

## EBNF replacement

Code: `grammar_generator/ebnf_generator_replacement.py`

Input: `generalized_input.json` file, where blanks contain replacement class information.

This grammar takes advantage of the additional information collected from the replacement phase. The internal representation of the grammar has a `start` non-terminal, as well as two non-terminals for each replacement class.
- The `start` subrules are again built from generalized inputs.
- Each blank is replaced by an OR of its replacement classes and the `start` non-terminal; for example, a blank with replacement classes `digits` and `whitespaces` will be replaced by `(digits | whitespaces | start)` in the grammar.
- Each replacement class has two non-terminals: a singular version and a repeat version. For example, the `DIGIT` replacement class would have the rules `digits: digit | digit digits` and `digit: /0/ | /1/ | ... | /9/`.

An example of printing the grammar as is:
```
start: (digits|start) /\*/x (digits|start) | /\(/x (digits|start) /\)/x
digits: digit | digit digits
digit: /0/ | /1/ | ... | /9/
```

However, when instantiating the Lark parser, we translate the grammar to instead use Lark's builtin terminal classes.

```
start: (digits|start) /\*/x (digits|start) | /\(/x (digits|start) /\)/x
digits: INT
%import common.INT
```

A drawback to this method is that it may run out of program memory when instantiating the parser, especially if a blank has a lot of replacement classes. More specifically, in Lark's implementation (`lark/load_grammar.py`), there is the following function:
```python
    def expansion(self, tree):
        # rules_list unpacking
        # a : b (c|d) e
        #  -->
        # a : b c e | b d e
        #
        # In AST terms:
        # expansion(b, expansions(c, d), e)
        #   -->
        # expansions( expansion(b, c, e), expansion(b, d, e) )
        ...
```

This function will recursively expand OR'd rules. So, if a rule looks something like this:
```
start: /\{"/ (printables|digits|whitespaces|hexdigits|letters|alphanumerics|start) /":/ /\[/ (digits|start) /,/ (digits|start) /\],/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":/ /null,\ "/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":"/ (digits|whitespaces|hexdigits|letters|alphanumerics|punctuations|start) /\\/ (whitespaces|digits|start) /"\}/
  | /\{"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":\[\],/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":\{"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":\[\],/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":/ /\{"/ (digits|whitespaces|hexdigits|letters|alphanumerics|punctuations|start) /"/ /:/ /null,/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":/ (start) /\}/ /\}/ /\}/
  | /\[/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /",/ /false,/ /\{/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":/ (digits|start) /\-/ (digits|start) /,/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /":/ /true,/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /"/ /:\[/ (digits|start) /\],/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /\\/ (digits|whitespaces|hexdigits|alphanumerics|start) /\\/ /r/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /"/ /:/ /"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /"/ /\},/ (digits|start) /e/ (digits|start) /,"/ (digits|whitespaces|hexdigits|letters|alphanumerics|start) /"\]/
  | /\{"":/ (digits|start) /,/ /"\\u/ (whitespaces|punctuations|start)
```
then the stack will probably overflow. :(

