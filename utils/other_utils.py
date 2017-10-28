some_sequence = 0


def get_next_id():
    """
    ONLY for debug!
    :return:
    """
    global some_sequence
    some_sequence += 1
    return some_sequence