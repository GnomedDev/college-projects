from __future__ import annotations

import random
from typing import Callable, Optional, TypeVar

import sorts, searches

T = TypeVar("T")

def get_array() -> list[int]:
    length = int(input("Enter length of array: "))
    return [int(input(f"Enter number {i}: ")) for i in range(length)]


class MenuItem:
    def __init__(self, name: str, callback: Callable[[], None]):
        self.name = name
        self.callback = callback

class SearchingAlgorithm(MenuItem):
    def __init__(self, name: str, search: Callable[[list[int], int], Optional[int]]):
        self.name = name
        self.search = search

    def callback(self):
        to_search = get_array()
        item = int(input("Enter item to search for: "))

        index = self.search(to_search, item)
        if index is None:
            print(f"{item} not found in array")
        else:
            print(f"{item} found at index {index}")

class SortingAlgorithm(MenuItem):
    def __init__(self, name: str, sort: Callable[[list[int]], Optional[list[int]]]):
        self.name = name
        self.sort = sort

    def callback(self):
        unsorted = get_array()
        sorted = self.sort(unsorted)

        # If the sort function returns None, the sort is inplace, so unsorted is now
        # a sorted array and should be returned back. This allows the `sort` to not
        # clutter itself with the output of the program
        if sorted is None:
            sorted = unsorted

        print("Sorted array is:", ", ".join(map(str, sorted)))

def factorial_wrapper():
    n = int(input("Number to apply factorial to: "))
    print(f"Factorial of {n} is {factorial(n)}")

def factorial(n: int) -> int:
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

def test_all():
    def random_array() -> list[int]:
        return [random.randint(0, 10) for _ in range(5)]

    test_arr = random_array()
    test_arr.sort()

    test_item = random.choice(test_arr)
    correct_index = test_arr.index(test_item)

    assert correct_index != -1

    print(f"Testing linear search with array {test_arr} and item {test_item}")
    assert searches.linear_search(test_arr, test_item) == correct_index
    print(f"Testing binary search with array {test_arr} and item {test_item}")
    assert searches.binary_search(test_arr, test_item) == correct_index

    for sort in sorts.__all__:
        rand_arr = random_array()
        print(f"Testing {sort} with {rand_arr}")

        if (sorted_arr := getattr(sorts, sort)(rand_arr)) is None:
            sorted_arr = rand_arr

        assert sorted_arr == sorted(rand_arr)

main_menu = (
    MenuItem("Factorial", factorial_wrapper),
    SearchingAlgorithm("Linear Search", searches.linear_search),
    SearchingAlgorithm("Binary Search", searches.binary_search),
    SortingAlgorithm("Bubble Sort", sorts.bubble_sort),
    SortingAlgorithm("Insertion Sort", sorts.insertion_sort),
    SortingAlgorithm("Merge Sort", sorts.merge_sort),
    MenuItem("Run tests", test_all),
)

print("Select an option:")
print("\n".join(f"{i}. {item.name}" for i, item in enumerate(main_menu, 1)))

choice = int(input("\n"))
main_menu[choice - 1].callback()
