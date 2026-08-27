from time import sleep
import numpy as np
from qcodes import Parameter


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

class StoredParameter(Parameter):
    """
    A parameter whose value. Set changes the value, get returns the value.
    If it is linked to another parameter, then par.update() will update the stored value by calling the underlying parameter
    You can check to see if the current value is within a given tolerance of the set value 
    
    """
    def __init__(self, 
                param: Parameter = None,
                name: str = 'stored_param', 
                unit:str = 'SI',
                docstring = 'Stored callable + setable qcodes parameter'
                ):
        
        super().__init__(name=name, unit=unit, docstring=docstring)

        self._value = None
        self._par = param
        #This is used to update a StoredParameter to it's underlying QCodes parameter by calling the original QCodes parameter. 
        if param is not None:
            self._linked = True
            self.update = self._Update_linked_parameter

        else:
            self._linked = False


    def get_raw(self):
        """
        None -> value
        Returns the value of the stored parameter
        """
        return self._value

    def set_raw(self, val):
        """
        value -> None
        Sets the value of the stored parameter. Gives a warning if the 
        """
        if self._linked == True:
            print(f'Overwriting the value set by {self._par.full_name}')
        
        self._value = val

    def _Update_linked_parameter(self):
        """
        Updates the ._value by reading from the ._par which is linked to the stored parameter
        None -> None
        """
        if self._linked == False:
            print('No parameter is linked to this StoredParameter')
        elif self._linked == True:
            self._value = self._par.get()

        

class Sum:
    def __init__(self, name, param1: Parameter, param2: Parameter):
        """
        A Qcodes parameter which can be used to read the sum of two other parameters, or set the sum with a given fixed difference
        name: str 
        The name of the parameter. This will be what is recorded during sweeps of the parameters
        param1: Parameter
        A qcodes parameter 
        param2: Parameter
        A qcodes parameter
        """
        self.full_name = name
        self.p1 = param1
        self.p2 = param2
        self.summ = 0
        self.diff = 0

    def __call__(self, val=None):
        """
        val (None/Float) -> val (Float/None):
        If val is None, simply read the sum of param1 and param2. 
        If val is a Float then it will set param1 + param2 = val, while keeping param1-param2 fixed. 
        """
        if val is None:
            return self.p1() + self.p2()

        else:
            self.summ = val
            self.diff = self.p1() - self.p2()
            p1val = (self.summ + self.diff) / 2
            p2val = (self.summ - self.diff) / 2
            self.p1(p1val)
            self.p2(p2val)


class Diff:
    
    def __init__(self, name, param1, param2):
        """
        A Qcodes parameter which can be used to read the difference of two other parameters, or set the difference with a given fixed difference
        name: str 
        The name of the parameter. This will be what is recorded during sweeps of the parameters
        param1: Parameter
        A qcodes parameter 
        param2: Parameter
        A qcodes parameter
        """ 

        self.full_name = name
        self.p1 = param1
        self.p2 = param2
        self.summ = 0
        self.diff = 0

    def __call__(self, val=None):
        """
        val (None/Float) -> val (Float/None):
        If val is None, simply read the difference of param1 and param2. 
        If val is a Float then it will set param1 - param2 = val, while keeping param1 + param2 fixed. 
        """ 
        if val is None:
            return self.p1() - self.p2()
        else:
            self.diff = val
            sumval = self.p1() + self.p2()
            p1val = (sumval + self.diff) / 2
            p2val = (sumval - self.diff) / 2
            self.p1(p1val)
            self.p2(p2val)