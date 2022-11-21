import time
import re
import random
from typing import List, Tuple, Union


def log(*args, **kwargs):
    """Log the fuzzing results"""
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}]", *args, **kwargs)


def bytes_to_str(input_bytes: bytes) -> str:
    # return the 'original input string'
    return input_bytes.decode("utf-8")


def str_to_bytes(input_str: str) -> bytes:
    return bytes(input_str, "utf-8")

# referencing https://stackoverflow.com/questions/4664850/how-to-find-all-occurrences-of-a-substring
# TODO: maybe we don't need to find overlapping occurrences?
def find_all_overlapping_substr(input_bytes: bytes, pattern: bytes) -> List[Tuple[int, int]]:
    match_ranges = [(m.start(), m.start() + len(pattern))
                    for m in re.finditer(
            str_to_bytes(f'(?={re.escape(bytes_to_str(pattern))})'),
            input_bytes)
                    ]
    return match_ranges


def find_all_nonoverlapping_substr(input_bytes: bytes, pattern: bytes) -> List[Tuple[int, int]]:
    match_ranges = [(m.start(), m.start() + len(pattern))
                    for m in re.finditer(re.escape(pattern), input_bytes)]
    return match_ranges


def find_random_substring(input_bytes: bytes, strings: List[bytes]) -> Union[bytes, None]:
    # locates all substrings in the input that match strings from
    # the obtained dictionary and chooses one randomly
    matched = []
    for pattern in strings:
        if len(find_all_nonoverlapping_substr(input_bytes, pattern)) != 0:
            matched.append(pattern)
    return random.choice(matched) if len(matched) != 0 else None

def replace_random_instance(input_bytes: bytes, sub: bytes, rand: bytes):
    match_ranges = find_all_nonoverlapping_substr(input_bytes, sub)
    (start, end) = random.choice(match_ranges) # end is not inclusive
    return input_bytes[0:start] + rand + input_bytes[end:]


def replace_all_instances(input_bytes: bytes, sub: bytes, rand: bytes) -> bytes:
    match_ranges = find_all_nonoverlapping_substr(input_bytes, sub)
    if len(match_ranges) != 0:
        tokens = []
        start = 0
        for (match_start, match_end) in match_ranges:
            tokens.append(input_bytes[start: match_start])
            start = match_end
        tokens.append(input_bytes[start: len(input_bytes)])
        return rand.join(tokens)
    return input_bytes
