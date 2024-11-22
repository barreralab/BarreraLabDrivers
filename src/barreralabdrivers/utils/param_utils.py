import numpy as np
from time import sleep


def paramp(param, final=0, steps=40, sleep_time=0.05):
    """
    Smoothly transitions a parameter to a specified final value.

    Args:
        param (callable): A callable that gets and sets the parameter value.
        final (float): The target value to transition to.
    """
    points = np.linspace(param(), final, steps)
    for p in points:
        param(p)
        sleep(sleep_time)
