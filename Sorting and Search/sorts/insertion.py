def insertion_sort(arr: list[int]):
    for i, item in enumerate(arr):
        j = i - 1

        while j >= 0 and item < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = item
