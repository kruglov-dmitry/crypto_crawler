

def float_to_str(f):
    """
    :param f:   Float or Decimal number
    :return: to be represented within EXACT precision as string
    NOTE: For Decimal you may end up with following numbers:
    0.0019120000000000000710265180003943896736018359661102294921875
    """
    float_string = str(f).lower()   # For Decimal class that represent within capitalized notation: 1E-10 1e-10
    if 'e' in float_string:  # detect scientific notation
        digits, exp = float_string.split('e')
        digits = digits.replace('.', '').replace('-', '')
        exp = int(exp)
        zero_padding = '0' * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
        sign = '-' if f < 0 else ''
        if exp > 0:
            float_string = '{}{}{}.0'.format(sign, digits, zero_padding)
        else:
            float_string = '{}0.{}{}'.format(sign, zero_padding, digits)
    elif float_string[-2:] == ".0":
        float_string = float_string[:-2]
    return float_string


def truncate_float(float_num, n):
    str_repr = str(float_num)
    idx = str_repr.find('.')
    if idx > 0:
        return float(str_repr[0: 1 + idx + n])
    else:
        return float_num
