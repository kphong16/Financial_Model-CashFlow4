import pandas as pd
import numpy as np
import math
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd
from datetime import datetime
from datetime import timedelta


PY = 1/3.305785
class Area:
    def __init__(self, m2=None, py=None, roundunit=2):
        self.m2 = m2
        self.py = py
        self.roundunit = roundunit
        self._intlz()
        self.area = (self.m2, self.py)
    
    def _intlz(self):
        if all([any([self.m2, self.m2==0]), not self.py]):
            self.py = round(self.m2 * PY, self.roundunit)
        if all([any([self.py, self.py==0]), not self.m2]):
            self.m2 = round(self.py / PY, self.roundunit)


class EmptyClass:
    def __init__(self):
        pass
    
    def __getattr__(self, attr):
        return self.__dict__[attr]
    
    def __getitem__(self, key):
        return self.__dict__[key]


def is_iterable(data):
    if type(data) == str:
        return False
    try:
        _ = iter(data)
        return True
    except TypeError:
        return False
        

def limited(val, upper=None, lower=None):
    tmp_val = val
    
    if upper:
        if is_iterable(upper):
            for val_lmt in upper:
                tmp_val = min(tmp_val, val_lmt)
        else:
            tmp_val = min(tmp_val, upper)
    
    if lower:
        if is_iterable(lower):
            for val_lmt in lower:
                tmp_val = max(tmp_val, val_lmt)
        else:
            tmp_val = max(tmp_val, lower)
    return tmp_val
    
    
def rounding(df, rate=None):
    rslt_df = df.copy()
    for key, val in rslt_df.items():
        if rate and key in rate:
            rslt_df[key] = rslt_df[key] * 100
        if all([isinstance(x, (int, float)) for x in rslt_df[key]]):
            if all([abs(x) < 100 or pd.isnull(x) for x in rslt_df[key]]):
                rslt_df[key] = rslt_df[key].fillna(0).apply(lambda x: f"{x:,.2f}")
            else:
                rslt_df[key] = rslt_df[key].fillna(0).apply(lambda x: f"{x:,.0f}")
    return rslt_df
    
    
def log10(val):
    tmpval = 0
    while True:
        val = val / 10
        if val > 0.9:
            tmpval += 1
        else:
            return tmpval
            
            
def round_up(number:float, decimals:int=2):
    """
    Returns a value rounded up to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals == 0:
        return math.ceil(number)

    factor = 10 ** decimals
    return math.ceil(number * factor) / factor
    
    
def percent(val:float):
    return val / 100