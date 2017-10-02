import itertools


def get_all_combination(my_dict, max_len):
    """
    :param my_dict:
    :param max_len:
    :return: list of possible combination of dictionary keys
    """
    return map(list, itertools.combinations(my_dict.keys(), max_len))