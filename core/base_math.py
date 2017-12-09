import itertools


def get_all_combination(my_dict, max_len):
    """
    :param my_dict:
    :param max_len:
    :return: list of possible combination of dictionary values

    Example:
        wtf= {}
        wtf[1] = "UNO"
        wtf[2] = "TWO"
        wtf[3] = "THREE"
        wtf[3] = "FOUR"

        res = get_all_combination(wtf, 2)
        print res
        [[1, 2], [1, 3], [2, 3]]

    """
    return map(list, itertools.combinations(my_dict.keys(), max_len))


def get_all_permutation(my_dict, max_len):
    """
    :param my_dict:
    :param max_len:
    :return: list of possible permutation of dictionary values


    Example:
        wtf= {}
        wtf[1] = "UNO"
        wtf[2] = "TWO"
        wtf[3] = "THREE"
        wtf[3] = "FOUR"

        res = get_all_permutation(wtf, 2)
        print res
        [[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]]

    """
    return map(list, itertools.permutations(my_dict.keys(), max_len))