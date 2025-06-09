import math
import matplotlib as plt

def round_up(number: float) -> int:
    '''
    This function is going to take a float and return an integer
    by rounding up to the nearest int using the `math` library

    Args:
        number (float): original floating point number to round up

    Returns:
        number (int): original number rounded up to the nearest integer
    '''
    return math.ceil(number)


def my_plotter(ax, data1, data2, param_dict):
    """
    A helper function to make a graph.
    """
    out = ax.plot(data1, data2, **param_dict)
    return out