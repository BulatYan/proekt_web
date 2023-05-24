def mul_to_int(a, b):
    c = a * b
    if float(c).is_integer():
        return int(c)
    return c 