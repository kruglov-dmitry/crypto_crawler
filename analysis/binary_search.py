def binary_search(some_list, target, cmp_method):
    """

    Generic method that will return INDEX for insertion of `target` element into list `some_list`

    :param some_list: element must have implementation of __eq__ method
    :param target: elements to be inserted
    :param cmp_method:
    :return:

    """
    min_idx = 0
    max_idx = len(some_list) - 1
    mid_idx = (min_idx + max_idx) / 2

    if mid_idx < 0:
        return 0
    elif min_idx == max_idx:
        # i.e. single element
        if cmp_method(some_list[mid_idx], target):
            return mid_idx + 1
        return mid_idx

    while min_idx < max_idx:
        if some_list[mid_idx] == target:
            return mid_idx
        elif cmp_method(some_list[mid_idx], target):
            return mid_idx + 1 + binary_search(some_list[mid_idx + 1:], target, cmp_method)
        else:
            return binary_search(some_list[:mid_idx], target, cmp_method)
