import random
from typing import List


# Generates a string containing characters from each group
def generate(groups: List[str], length: int):
    result = ""
    for i in range(length):
        group = random.choice(groups)
        char = random.choice(group)
        result += char
    return result

def generate_real_number_str():
    num = random.randint(1, 1000000)
    den = random.randint(1, 1000000)
    result = str(num / den)
    return result

