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

#from pandas import (
#    date_range,
#    DatetimeIndex,
#    PeriodIndex,
    #RangeIndex,
#)

from datetime import (
    date,
    timedelta
)
from dateutil.relativedelta import relativedelta

#from .genfunc import is_iterable
__all__ = ['RangeIndex', 'DateIndex', 'date_range'] #, 'booleanloc', 'PrjtIndex']


def is_scalar(value):
    if isinstance(value, int):
        return True
    else:
        return False
        
def str_to_date(value):
    # date
    if isinstance(value, date):
        return value

    # date('-')
    value_lst = value.split('-')
    if len(value_lst) == 3:
        int_lst = [int(x) for x in value_lst]
        return date(*int_lst)
    elif len(value_lst) == 2:
        int_lst = [int(x) for x in value_lst]
        return date_monthend(*int_lst)
    
    # date('.')
    value_lst = value.split('.')
    if len(value_lst) == 3:
        int_lst = [int(x) for x in value_lst]
        return date(*int_lst)
    elif len(value_lst) == 2:
        int_lst = [int(x) for x in value_lst]
        return date_monthend(*int_lst)
        
    raise TypeError("Type of the data is not suitable.")
        
def date_monthend(year, month=None):
    if isinstance(year, date):
        dt = year
        return date_monthend(dt.year, dt.month)
        
    if isinstance(year, str):
        dt = year
        return date_monthend(str_to_date(dt))
    
    if month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        month_next = month + 1
        dt_next = date(year, month_next, 1)
        dt_monthend = dt_next - timedelta(days=1)
    elif month == 12:
        year_next = year + 1
        dt_next = date(year_next, 1, 1)
        dt_monthend = dt_next - timedelta(days=1)
    return dt_monthend

def date_next(dt, freq='M'):
    assert isinstance(dt, date)
    if freq=='M':
        if dt.month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
            month_next = dt.month + 1
            dt_next = date_monthend(dt.year, month_next)
        elif dt.month == 12:
            year_next = dt.year + 1
            dt_next = date_monthend(year_next, month=1)
        return dt_next
    if freq=='Y':
        dt_next = dt + relativedelta(years=1)
        return dt_next
    if freq=='D':
        dt_next = dt + timedelta(days=1)
        return dt_next
    
def is_samemonth(*args):
    if len(args) < 2:
        raise ValueError("Number of values are not enough.")
    year_crit = args[0].year
    month_crit = args[0].month
    
    for val in args[1:len(args)]:
        if val.year != year_crit:
            return False
        if val.month != month_crit:
            return False
    return True

def all_none(*args):
    tmp_lst = [x==None for x in args]
    return all(tmp_lst)
    
def any_none(*args):
    tmp_lst = [x==None for x in args]
    return any(tmp_lst)

def allnot_none(*args):
    tmp_lst = [x!=None for x in args]
    return all(tmp_lst)
    
def anynot_none(*args):
    tmp_lst = [x!=None for x in args]
    return any(tmp_lst)


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
        ):
        
        # RangeIndex
        if isinstance(start, RangeIndex):
            return start.copy(name=name)
        elif isinstance(start, range):
            return cls._simple_new(start, name)
            
        # validate the arguments
        if all_none(start, stop, step):
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
    def _simple_new(cls, values: range, name=None):
        result = object.__new__(cls)
        
        assert isinstance(values, (range, RangeIndex))
        
        result._data = values
        result._range = values
        result._name = name
        result._cache = {}
        #result._reset_identity()
        return result
        
    @classmethod
    def _ensure_int(cls, value):
        new_value = int(value)
        assert new_value == value
        return new_value
            
    def copy(self, name=None):
        try:
            casted = self._data
        except (TypeError, ValueError) as err:
            raise TypeError(
                f"Cannot cast {type(self).__name__}"
                ) from err
        if name is None:
            name = self.name
        return RangeIndex(casted, name=name)
    
    def __len__(self) -> int:
        """
        Return the length of the Index.
        """
        return len(self._data)
    
    def __setitem__(self, key, value):
        raise TypeError("Index does not support mutable operations")
    
    def __getitem__(self, key):
        getitem = self._data.__getitem__
        
        if is_scalar(key):
            return getitem(key)
        
        if isinstance(key, slice):
            result = getitem(key)
            return type(self)._simple_new(result, name=self.name)
        
    def __repr__(self):
        """
        Return a string representation for this object.
        """
        klass_name = type(self).__name__
        data = str(self._data)
        return f"{klass_name}({data})"
    
    @property
    def values(self):
        return self._data
    
    @property
    def data(self):
        return self._data
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
        
    
    
class DateIndex():
    def __new__(
        cls,
        data=None,
        freq=None,
        name=None,
        ):
        
        # DateIndex
        if isinstance(data, DateIndex):
            dtarr = data.copy(name=name)
            
        # string
        elif isinstance(data, str):
            dtarr = [str_to_date(data)]
            
        # list
        elif isinstance(data, list):
            new_lst = []
            for val in data:
                if isinstance(val, date):
                    new_lst.append(val)
                elif isinstance(val, str):
                    new_lst.append(str_to_date(val))
            dtarr = new_lst
        else:
            raise TypeError("Input data type error.")
            
        subarr = cls._simple_new(dtarr, name=name)
        return subarr
        
    @classmethod
    def _simple_new(cls, values: list, name=None):
        result = object.__new__(cls)
        
        assert isinstance(values, (list, DateIndex))
        
        result._data = values
        result._name = name
        result._cache = {}
        return result
        
    def copy(self, name=None):
        try:
            casted = self._data
        except (TypeError, ValueError) as err:
            raise TypeError(
                f"Cannot cast {type(self).__name__}"
                ) from err
        if name is None:
            name = self.name
        return DateIndex(casted, name=name)        
    
    def __len__(self) -> int:
        """
        Return the length of the Index.
        """
        return len(self._data)
    
    def __setitem__(self, key, value):
        raise TypeError("Index does not support mutable operations")
    
    def __getitem__(self, key):
        getitem = self._data.__getitem__
        
        if is_scalar(key):
            return getitem(key)
        
        if isinstance(key, slice):
            result = getitem(key)
            return type(self)._simple_new(result, name=self.name)
        
    def __repr__(self):
        """
        Return a string representation for this object.
        """
        klass_name = type(self).__name__
        data = str(self._data)
        return f"{klass_name}({data})"
    
    @property
    def values(self):
        return self._data
    
    @property
    def data(self):
        return self._data
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
            
            
def date_range(
    start=None,
    end=None,
    periods=None,
    freq=None,
    name=None,
    ) -> DateIndex:
    """
    Return a fixed frequency DateIndex.
    
    Parameters
    ----------
    start : str or datetime.date
        Left bound for generating dates.
    end : str or datetime.date
        Right bound for generating dates.
    periods : int, optional
        Number of periods to generate.
    freq : str or DateOffset, default 'M'
    
    Returns
    -------
    rng : DateIndex
    """
    
    if freq is None and any_none(periods, start, end):
        freq = "M"
    
    if allnot_none(start, end, periods):
        raise ValueError("There are too many data.")
    elif allnot_none(start, periods):
        dtarr = []
        if periods > 0:
            start = str_to_date(start)
            dtarr.append(start)
            dt_next = start
        for no in range(1, periods):
            dt_next = date_next(dt_next, freq=freq)
            dtarr.append(dt_next)
    elif allnot_none(end, periods):
        end = str_to_date(end)
        start = end - relativedelta(months=(periods-1))
        return date_range(start, periods=periods)
    elif allnot_none(start, end):
        dtarr = []
        start = str_to_date(start)
        if isinstance(end, int):
            periods = end
            if periods > 0:
                dtarr.append(start)
                dt_next = start
            for no in range(1, periods):
                dt_next = date_next(dt_next, freq=freq)
                dtarr.append(dt_next)
        else:
            end = str_to_date(end)
            if end == start:
                dtarr.append(start)
            elif end > start:
                dtarr.append(start)
                dt_next = start
                while True:
                    if dt_next >= end:
                        break
                    dt_next = date_next(dt_next, freq=freq)
                    dtarr.append(dt_next)
            elif end < start:
                raise ValueError("The end date is before the start date.")
        
    subarr = DateIndex._simple_new(dtarr, name=name)
    return subarr














































