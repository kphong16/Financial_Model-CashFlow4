#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong

General functions for cafle.

Attributes
----------
PY : the area unit used in Korea

Modules
-------
Area : transform between m2 and PY units. 
"""

import math
from datetime import datetime
from functools import wraps
from pandas.api.types import is_numeric_dtype

__all__ = ['PY', 'Area', 'EmptyClass', 'is_iterable', 'limited', 'rounding', 
           'print_rounding', 'round_up', 'log10']

PY = 1/3.305785
# PY("pyung") is the area unit used in Korea.

class Area:
    """
    Transform between m2 and PY units.
    
    Parameters
    ----------
    m2 : int, float, default None
    py : int, float, default None
    roundunit : int, default 2
    
    Attributes
    ----------
    area : tuple
        return a tuple of m2, py.
    m2 : float
        value of m2 unit
    py : float
        value of py unit
        
    Examples
    --------
    >>> ar = Area(1000)
    >>> ar.area
        (1000, 302.5)
    >>> ar.py
        302.5
    >>> ar.m2
        1000
    """
    def __init__(self, m2=None, py=None, roundunit=2):
        self._m2 = m2
        self._py = py
        self._roundunit = roundunit
        self._intlz()
        
    def _intlz(self):
        if all([self._m2 is not None, self._py is None]):
            self._py = round(self._m2 * PY, self._roundunit)
        if all([self._m2 is None, self._py is not None]):
            self._m2 = round(self._py / PY, self._roundunit)
            
    @property
    def area(self):
        return (self._m2, self._py)
        
    @property
    def m2(self):
        return self._m2
        
    @property
    def py(self):
        return self._py
        
        
class EmptyClass:
    def __init__(self):
        pass
        
    def __getattr__(self, attr):
        return self.__dict__[attr]
        
    def __getitem__(self, key):
        return self.__dict__[key]

    @property
    def dict(self):
        return self.__dict__

    @property
    def keys(self):
        return self.__dict__.keys()
        

def is_scalar(data):
    if isinstance(data, (str, int, float)):
        return True
    else:
        return False


def is_iterable(data):
    if type(data) == str:
        return False
    try:
        _ = iter(data)
        return True
    except TypeError:
        return False
        
        
def limited(val, upper=None, lower=None):
    """
    Adjust the input value between "upper" and "lower" values.
    
    Parameters
    ----------
    val : int, float
        input value
    upper : int, float, list, tuple
        the criteria for distinguishing upper values
    lower : int, float, list, tuple
        the criteria for distinguishing lower values
    
    Return
    ------
    Adjusted value between upper values and lower values.
        
    Examples
    --------
    >>> limited(100, upper=90, lower=50)
        90
    >>> limited(30, lower=[10, 40])
        40
    """

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
    for key, item in rslt_df.items():
        if rate is not None and key in rate:
            rslt_df[key] = rslt_df[key] * 100
        if all([isinstance(val, (int, float)) for val in rslt_df[key]]):
            rslt_df[key] = rslt_df[key].fillna(0).apply(lambda x: f"{x:,.0f}")
    return rslt_df
    
    
def print_rounding(df):
    """
    Apply a separator to the number and round the number.
    
    Parameters
    ----------
    df : DataFrame
    
    Return
    ------
    DataFrame rounded and applied a separator to the number
        
    Examples
    --------
    >>> df = DataFrame({'a':[100000,     200000    ], 
                        'b':[100000.123, 200000.321], 
                        'c':['abc',      'cde'     ]})
    >>> print_rounding(df)
                 a        b    c
        0  100,000  100,000  abc
        1  200,000  200,000  cde
    """
    rslt_df = df.copy()
    for key, item in rslt_df.items():
        if is_numeric_dtype(item):
            rslt_df[key] = rslt_df[key].fillna(0).apply(lambda x: f"{x:,.0f}")
    return rslt_df
        
        
def round_up(number:float, decimals:int=2):
    """
    Return a value rounded up to a specific number of decimal places.
    
    Parameters
    ----------
    number : int, float
    decimals : int
    
    Return
    ------
    float
        
    Examples
    --------
    >>> round_up(123.1231, 1)
        123.2
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals == 0:
        return math.ceil(number)
        
    factor = 10 ** decimals
    return math.ceil(number * factor) / factor

    
def log10(val):
    tmpval = 0
    while True:
        val = val / 10
        if val > 0.9:
            tmpval += 1
        else:
            return tmpval
    

# Decorator
def listwrapper(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        is_iter = True
        for arg in args:
            if is_iterable(arg) is False:
                is_iter = False
        for item in kwargs.values():
            if is_iterable(item) is False:
                is_iter = False
                
        if is_iter is True:
            ilen = 0
            for arg in args:
                if len(arg) > ilen:
                    ilen = len(arg)
            for item in kwargs.values():
                if len(item) > ilen:
                    ilen = len(item)
            
            for i in range(ilen):
                new_args = []
                new_kwargs = {}
                
                for val in args:
                    new_args = new_args + [val[i]]
                new_args = tuple(new_args)
                
                for key, item in kwargs.items():
                    new_kwargs[key] = item 
                
                func(self, *new_args, **new_kwargs)
        else:
            new_args = args
            new_kwargs = kwargs
            func(self, *new_args, **new_kwargs)
    return wrapped
    


"""
# Decorator
def listwrapper(func):
    @wraps(func)
    def wrapped(self, *args):
        is_iter = True
        for arg in args:
            if is_iterable(arg) is False:
                is_iter = False
        if is_iter is True:
            ilen = len(args[0])
            for i in range(ilen):
                new_args = []
                for val in args:
                    new_args = new_args + [val[i]]
                new_args = tuple(new_args)
                func(self, *new_args)
        else:
            new_args = args
            func(self, *new_args)
    return wrapped
"""
    
    
    
    
    
    
