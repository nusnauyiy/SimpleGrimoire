# Replacement Classes

Code: `models/ReplaceClass.py`

-----

Replacement classes are used in Replacement Grimoire. They are based on [python string constants](https://docs.python.org/3/library/string.html). 

### DIGIT
The digits `0123456789`.


### HEXDIGIT

The hexdigits `0123456789abcdefABCDEF`.

### LETTER

The letters `abdcefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`.

### WHITESPACE

All ASCII characters that are considered whitespace, including the characters space, tab, linefeed, return, formfeed, and vertical tab. (from python docs). 

### PUNCTUATION

The characters ``!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~``.

### ALPHANUMERIC

Union of LETTER and DIGIT classes.

### PRINTABLE

Union of LETTER, DIGIT, WHITESPACE, and PUNCTUATION classes.
