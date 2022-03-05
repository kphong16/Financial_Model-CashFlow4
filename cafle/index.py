#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong

INDEX

Modules
-------
Index : Create and manage an array of dates
PrjtIndex : Create and manage index objects

Methods
-------
booleanloc : Return boolean array of data which is in array
"""

import pandas as pd
import numpy as np

from pandas import (
    date_range,
    DatetimeIndex,
    PeriodIndex,
    RangeIndex,
)

from datetime import (
    date,
    datetime
)

from .genfunc import is_iterable

__all__ = ['Index', 'booleanloc', 'PrjtIndex']


class RangeIndex():
    """
    Parameters
    ----------
    start : int(default:0), range, RangeIndex instance
      If int and 'stop' is not given, interpreted as 'stop' instead.
    stop : int(default:0)
    step : int(default:1)
    
    
    Attributes
    ----------
    start
    stop
    step
    
    Methods
    -------
    from_range
    """
    def __new__(
        cls, 
        start=None,
        stop=None,
        step=None,
        name=None,
        ) -> RangeIndex:
        
        # RangeIndex
        if isinstance(start, RangeIndex):
            return start.copy(name=name)
        elif isinstance(start, range):
            return cls._simple_new(start, name)
            
        # validate the arguments
        if start is None and stop is None and step is None:
            raise TypeError("RangeIndex(...) must be called with integers")
            
        start = cls._ensure_int(start) if start is not None else 0
        
        if stop is None:
            start, stop = 0, start
        else:
            stop = cls._ensure_int(stop)
            
        step = cls._ensure_int(step) if step is not None else 1
        if step == 0:
            raise ValueError("Step must not be zero")
            
        rng = range(start, stop, step)
        return cls._simple_new(rng, name=name)
        
            
    @classmethod
    def _simple_new(cls, values: range, name=None) -> RangeIndex:
        result = object.__new__(cls)
        
        assert isinstance(values, range)
        
        result._range = values
        result._name = name
        result._cache = {}
        result._reset_identity()
        return result
        
    @classmethod
    def _ensure_int(cls, value):
        new_value = int(value)
        assert new_value == value
        return new_value
            
    def copy(
        self,
        name=None
        ):
        
        try:
            casted = self._data
        except (TypeError, ValueError) as err:
            raise TypeError(
                f"Cannot cast {type(self).__name__}"
                ) from err
        return RangeIndex(casted, name=self.name)        
         



