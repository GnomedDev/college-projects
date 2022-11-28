def merge_sort(arr: list[int]):
    if len(arr) <= 1:
        return

    # Finding the mid of the array
    mid = len(arr)//2

    left = arr[:mid]
    right = arr[mid:]

    merge_sort(left)
    merge_sort(right)
    merge(left, right, arr)

def merge(left: list[int], right: list[int], arr: list[int]):
    i = j = k = 0

    # Loop over left and right simultaneously
    # advancing the indexes i and j based on
    # the comparison of the values at those indexes
    while i < len(left) and j < len(right):
        left_elm = left[i]
        right_elm = right[j]

        if left_elm <= right_elm:
            arr[k] = left_elm
            i += 1
        else:
            arr[k] = right_elm
            j += 1

        k += 1

    # Once either left or right has finished being looped over
    # the rest of the other array can be appended to
    # the end of the array
    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1
    
    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1
