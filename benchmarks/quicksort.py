"""
An implementation of python quicksort.
"""

from typing import List


def _quick_sort_internal(array: List[int]):
    """Sort the array by using quicksort."""
    if len(array) < 2 : 
        return array
    
    pivot = array[0]
    left_hand_range = []
    pivot_range = [pivot]
    right_hand_range = []
    for elem in array[1:]:
        if elem < pivot:
            left_hand_range.append(elem)
        elif elem == pivot:
            pivot_range.append(elem)
        else:
            right_hand_range.append(elem)
    left_hand_range = _quick_sort_internal(left_hand_range)
    right_hand_range = _quick_sort_internal(right_hand_range)
    return left_hand_range + pivot_range + right_hand_range


def test_one_input(input_data: bytes):
    array = [c for c in input_data]
    sorted_array =  _quick_sort_internal(array)
    assert(sorted_array == sorted(array))
