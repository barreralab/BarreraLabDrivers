import numpy as np
from time import sleep


def paramp(
    params: tuple,
    final: tuple = (0),
    steps: int = 40,
    sleep_time: float = 0.05,
    track=True,
):
    """
    Smoothly transitions a group of parameters to a specified final value.

    Args:
        param (tuple of callables): A callable that gets and sets the parameter value.
        final (tuple of floats): The target value to transition to.
        steps (int): the number of steps which the paramp will take
        sleep_time (float): time per step (s)
        track (bool): Choose whether the paramaters ramp at the same time or sequentially

    """

    # this is a legacy function which ensures that passing a single callable as params will work
    if type(params) != tuple:
        points = np.linspace(params(), final, steps)
        for point in points:
            params(point)
            sleep(sleep_time)

    # this section will handle tuples of params and final
    if type(params) == tuple:
        points = {}
        # this loop defines the points for user defined endpoint
        if final != (0):
            if len(final) != len(params):
                raise ValueError("final and param must be the same length")
            for i in range(len(params)):
                par = params[i]
                points[i] = np.linspace(par(), final[i], steps)

        # this loop defines points for ramping to zero
        elif final == (0):
            for i in range(len(params)):
                par = params[i]
                points[i] = np.linspace(par(), 0, steps)

        # This ramps the parameters together
        if track == True:
            for step in range(steps):
                for i in range(len(params)):
                    par = params[i]
                    par(points[i][step])
                sleep(sleep_time)

        # This ramps the parameters sequentially
        elif track == False:
            for i in range(len(params)):
                for point in points[i]:
                    par = params[i]
                    par(point)
                    sleep(sleep_time)
