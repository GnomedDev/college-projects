def bubble_sort(arr: list[int]):
    swapped = True
    while swapped:
        swapped = False
        for i, item in enumerate(arr):
            try:
                next_item = arr[i + 1]
            except IndexError:
                continue

            if item > next_item:
                arr[i + 1] = item
                arr[i] = next_item

                swapped = True
