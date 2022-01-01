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

from datetime import datetime
from datetime import date

from .genfunc import is_iterable

__all__ = ['Index', 'booleanloc', 'PrjtIndex']

class Index(object):
    """
    Parameters
    ----------
    start : date, ex) '2021-01', '2021-01-01'
    end : date, ex) '2021-01', '2021-01-01'
    periods : int, ex) 12 <- for twelve months
    freq : str, frequency of data, default "M", ex) 'M', 'D'
    + 'D' : Day
    + 'B' : Business Day
    + 'M' : MonthEnd
    + 'BM' : Business MonthEnd
    + 'MS' : MonthBegin
    + 'BMS' : Business MonthBegin
    + 'WOM-1MON', 'WOM-2MON', ... : Week of Month(1st monday of every month)
      
    Attributes
    ----------
    arr : Array of datetime date objects
    idxno : Index numbering of array
    year : Array of year on date array
    month : Array of month on date array
    day : Array of day on date array
    
    Methods
    -------
    __getitem__ : Return the number of the index or the date object
    __len__ : Return the lenth of array
    isloc : Check data(year, month, day) is in the array and return 
        the boolean array.
    noloc : Check data(year, month, day) is in the array and return
        the index number array.
    valloc : Check data(year, month, day) is in the array and return
        the date object array.
    """
    
    def __init__(self, start    = None,
                       end      = None,
                       periods  = None,
                       freq     = 'M',
                       ):
        self._start = start
        self._end = end
        self._periods = periods
        self._freq = freq
        self._range = pd.date_range(start, end, periods, freq)
        self._idxno = np.arange(len(self._range))
        
    @property
    def arr(self):
        return self._range.date
        
    def __getitem__(self, val):
        """
        If val is an integer, return the date which is in location index.
        If val is a date, return the location index number.
        If val is a string, seperate the string to tuple(year, month, day).
            And apply valloc function to return the list of dates.
        
        Parameters
        ----------
        val: int, slice, date, date like string, 
            ex) 0, 1:3, datetime.date(2021, 4, 30), "2021-04", "2021-04-30"
        
        Return
        ------
        datetime.date
        Array of datetime.date
        location index number
        
        Examples
        --------
        >>> idx = Index("2021.01", "2022.12")
        >>> idx[0]
            datetime.date(2021, 1, 31)
        >>> idx[1:3]
            array([datetime.date(2021, 2, 28), datetime.date(2021, 3, 31)],
            dtype=object)
        >>> idx[datetime.date(2021, 4, 30)]
            3
        >>> idx["2021-04"]
            array([datetime.date(2021, 4, 30)], dtype=object)
        >>> idx["2021"]
            array([datetime.date(2021, 1, 31), datetime.date(2021, 2, 28),
            datetime.date(2021, 3, 31), datetime.date(2021, 4, 30),
            ...
            datetime.date(2021, 11, 30)], dtype=object)
        """
        if isinstance(val, date):
            tmparr = self._idxno[self.arr == val]
            return tmparr[0]
        if isinstance(val, str):
            strpval = strpdate(val)
            if is_iterable(strpval):
                return self.valloc(*strpval)
            return self.valloc(strpval)
        return self.arr[val]
        
    def __len__(self):
        return len(self.arr)
        
    @property
    def year(self):
        return self._range.year
        
    @property
    def month(self):
        return self._range.month
        
    @property
    def day(self):
        return self._range.day
        
    @property
    def idxno(self):
        return self._idxno
        
    def isloc(self, year=None, month=None, day=None):
        """
        Check data(year, month, day) is in the array and return the boolean array result.
        
        Parameters
        ----------
        year: int, list, tuple, ex) 2021, 2022, [2021, 2022]
        month: int, list, tuple, ex) 6, 7, [6, 7]
        day: int, list, tuple, ex) 3, 30, [3, 30]
        
        Return
        ------
        Array of boolean
        
        Examples
        --------
        >>> idx = Index("2021.01", "2022.12")
        >>> idx.isloc(month=[6, 7, 8])
            array([False, False, False, False, False,  True,  True,  True,
            False, False, False, False, False, False, False, False, False,
            True, True, True, False, False, False])
        """
        isyear = _getblnloc(self.year, year)
        ismonth = _getblnloc(self.month, month)
        isday = _getblnloc(self.day, day)
        
        return isyear & ismonth & isday
                
    def noloc(self, year=None, month=None, day=None):
        """
        Check data(year, month, day) is in the array and return the index number array result.
        
        Parameters
        ----------
        year: int, list, tuple, ex) 2021, 2022, [2021, 2022]
        month: int, list, tuple, ex) 6, 7, [6, 7]
        day: int, list, tuple, ex) 3, 30, [3, 30]
        
        Return
        ------
        Array of index number
        
        Examples
        --------
        >>> idx = Index("2021.01", "2022.12")
        >>> idx.noloc(month=[6, 7, 8])
            array([ 5,  6,  7, 17, 18, 19])
        """
        blnloc = self.isloc(year, month, day)
        return self._idxno[blnloc]
        
    def valloc(self, year=None, month=None, day=None):
        """
        Check data(year, month, day) is in the array and return the date object array result.
        
        Parameters
        ----------
        year: int, list, tuple, ex) 2021, 2022, [2021, 2022]
        month: int, list, tuple, ex) 6, 7, [6, 7]
        day: int, list, tuple, ex) 3, 30, [3, 30]
        
        Return
        ------
        Array of datetime.date objects
        
        Examples
        --------
        >>> idx = Index("2021.01", "2022.12")
        >>> idx.valloc(month=[6, 7, 8])
            array([datetime.date(2021, 6, 30), datetime.date(2021, 7, 31),
            datetime.date(2021, 8, 31), datetime.date(2022, 6, 30),
            datetime.date(2022, 7, 31), datetime.date(2022, 8, 31)],
            dtype=object)
        """
        tmpno = self.noloc(year, month, day)
        return self[tmpno]
        
def strpdate(arg):
    if "-" in arg:
        args = arg.split("-")
        if len(args) == 2:
            year = int(args[0])
            month = int(args[1])
            return (year, month)
        if len(args) == 3:
            year = int(args[0])
            month = int(args[1])
            day = int(args[2])
            return (year, month, day)
    elif "." in arg:
        args = arg.split(".")
        if len(args) == 2:
            year = int(args[0])
            month = int(args[1])
            return (year, month)
        if len(args) == 3:
            year = int(args[0])
            month = int(args[1])
            day = int(args[2])
            return (year, month, day)
    else:
        year = int(arg)
        return (year)
        
    
def _getblnloc(array, val):
    """
    Get boolean location
    """
    if val is None:
        return [True]
    else:
        return booleanloc(array)[val]
        
class booleanloc():
    """
    Return boolean array of data which is in array
    
    Parameters
    ----------
    array : data array
    
    Returns
    -------
    array : boolean array
    
    Examples
    --------
    tmp = booleanloc(np.array([10, 20, 30]))
    tmp[10]
    >>> array([True, False, False])
    tmp[[20, 30]]
    >>> array([False, True, True])
    """
    def __init__(self, array):
        self.array = array
        
    def __getitem__(self, data):
        if is_iterable(data):
            return self.loopiniter(self.array, data)
        else:
            return self.array == data
    
    @staticmethod
    def loopiniter(array, data):
        tmp = [False]
        for val in data:
            blnarray = array == val
            tmp = tmp | blnarray
        return tmp
        

class PrjtIndex(object):
    """
    Parameters
    ----------
    idxname : list of string, ex) ['prjt', 'cstrn', 'loan']
    start : list of date, ex) ['2021-01', '2021-01', '2021-01']
    end : list of date, ex) ['2022-12', '2022-12', '2022-12']
    periods : list of int, ex) [30, 24, 24]
    freq : str, frequency of data, default "M", ex) 'M', 'D'
    + 'D' : Day
    + 'B' : Business Day
    + 'M' : MonthEnd
    + 'BM' : Business MonthEnd
    + 'MS' : MonthBegin
    + 'BMS' : Business MonthBegin
    + 'WOM-1MON', 'WOM-2MON', ... : Week of Month(1st monday of every month)
    mainidxno : int, default 0
        Set main index
        If it is 0 then idxname[0] be main index.
      
    Attributes
    ----------
    dct : Dictionary of indexes
    arr : Array of datetime date objects from main index
    idxno : Index numbering of array from main index
    year : Array of year on date array from main index
    month : Array of month on date array from main index
    day : Array of day on date array from main index
    
    Methods
    -------
    All of the below methods operate under the main index.
    __getitem__ : Return the number of the index or the date object
    __len__ : Return the lenth of array
    isloc : Check data(year, month, day) is in the array and return 
        the boolean array.
    noloc : Check data(year, month, day) is in the array and return
        the index number array.
    valloc : Check data(year, month, day) is in the array and return
        the date object array.
    """
    def __init__(self,
                 idxname,
                 start = None,
                 end = None,
                 periods = None,
                 freq: str = 'M',
                 mainidxno = 0
                 ):
        self._idxname = idxname
        self._start = start
        self._end = end
        self._periods = periods
        self._freq = freq
        self._mainidxno = mainidxno
        self.dct = {}
        
        self._intlz()
        
    def _intlz(self):
        self._setidx()
        self.main = self.dct[self._idxname[self._mainidxno]]
        
    def _setidx(self):
        """
        Set each index on idxname list.
        Set attributes on each index
        """
        for no, idxnm in enumerate(self._idxname):
            idxistnc = Index(start = self._isNone(self._start, no),
                             end = self._isNone(self._end, no),
                             periods = self._isNone(self._periods, no),
                             freq = self._freq)
            self.dct[idxnm] = idxistnc
            setattr(self, idxnm, idxistnc)
            
    def _isNone(self, val, no):
        """
        If val is None, return None.
        If val has a data, return val[no]
        """
        if val is not None:
            return val[no]
        else:
            return val
            
    def __getitem__(self, val):
        """
        If val is a string and the string is in dictionary, 
            return the index of which name is the string.
        If val is a string, seperate the string to tuple(year, month, day).
            And apply valloc function to return the list of dates.
        If val is an integer, return the date which is in location index.
        If val is a date, return the location index number.
        
        Parameters
        ----------
        val: str, int, slice, date, ex) "loan", 0, 1:3, 
            datetime.date(2021, 4, 30)
        
        Return
        ------
        Index object
        datetime.date
        Array of datetime.date
        location index number
        
        Examples
        --------
        >>> prjtidx = cf.PrjtIndex(idxname=['prjt', 'cstrn', 'loan'],
                       start=['2021-01', '2021-05', '2021-07'],
                       periods=[18, 10, 8])
        >>> prjtidx['cstrn'].arr
            array([datetime.date(2021, 5, 31), datetime.date(2021, 6, 30),
            datetime.date(2021, 7, 31), datetime.date(2021, 8, 31),
            datetime.date(2021, 9, 30), datetime.date(2021, 10, 31),
            datetime.date(2021, 11, 30), datetime.date(2021, 12, 31),
            datetime.date(2022, 1, 31), datetime.date(2022, 2, 28)],
            dtype=object)
        >>> prjtidx[0]
            datetime.date(2021, 1, 31)
        >>> prjtidx[1:3]
            array([datetime.date(2021, 2, 28), datetime.date(2021, 3, 31)],
            dtype=object)
        >>> prjtidx[datetime.date(2021, 4, 30)]
            3
        >>> idx["2021-04"]
            array([datetime.date(2021, 4, 30)], dtype=object)
        >>> idx["2021"]
            array([datetime.date(2021, 1, 31), datetime.date(2021, 2, 28),
            datetime.date(2021, 3, 31), datetime.date(2021, 4, 30),
            ...
            datetime.date(2021, 11, 30)], dtype=object)
        """
        if isinstance(val, str):
            if val in self.dct:
                return self.dct[val]
            strpval = strpdate(val)
            if is_iterable(strpval):
                return self.valloc(*strpval)
            return self.valloc(strpval)
            
        if isinstance(val, date):
            return self.main[val]
        return self.main[val]

    def __len__(self):
        return len(self.main)
    
    @property
    def arr(self):
        return self.main.arr
    
    @property
    def year(self):
        return self.main.year
    
    @property
    def month(self):
        return self.main.month
        
    @property
    def day(self):
        return self.main.day
        
    @property
    def idxno(self):
        return self.main.idxno
        
    def isloc(self, year=None, month=None, day=None):
        """
        Check data(year, month, day) is in the array and return the boolean array result.
        
        Parameters
        ----------
        year: int, list, tuple, ex) 2021, 2022, [2021, 2022]
        month: int, list, tuple, ex) 6, 7, [6, 7]
        day: int, list, tuple, ex) 3, 30, [3, 30]
        
        Return
        ------
        Array of boolean
        
        Examples
        --------
        >>> prjtidx = PrjtIndex(["prjt"], ["2021.01"], ["2022.12"])
        >>> prjtidx.isloc(month=[6, 7, 8])
            array([False, False, False, False, False,  True,  True,  True,
            False, False, False, False, False, False, False, False, False,
            True, True, True, False, False, False])
        """
        return self.main.isloc(year, month, day)
        
    def noloc(self, year=None, month=None, day=None):
        """
        Check data(year, month, day) is in the array and return the index number array result.
        
        Parameters
        ----------
        year: int, list, tuple, ex) 2021, 2022, [2021, 2022]
        month: int, list, tuple, ex) 6, 7, [6, 7]
        day: int, list, tuple, ex) 3, 30, [3, 30]
        
        Return
        ------
        Array of index number
        
        Examples
        --------
        >>> prjtidx = PrjtIndex(["prjt"], ["2021.01"], ["2022.12"])
        >>> prjtidx.noloc(month=[6, 7, 8])
            array([ 5,  6,  7, 17, 18, 19])
        """
        return self.main.noloc(year, month, day)

    def valloc(self, year=None, month=None, day=None):
        """
        Check data(year, month, day) is in the array and return the date object array result.
        
        Parameters
        ----------
        year: int, list, tuple, ex) 2021, 2022, [2021, 2022]
        month: int, list, tuple, ex) 6, 7, [6, 7]
        day: int, list, tuple, ex) 3, 30, [3, 30]
        
        Return
        ------
        Array of datetime.date objects
        
        Examples
        --------
        >>> prjtidx = PrjtIndex(["prjt"], ["2021.01"], ["2022.12"])
        >>> prjtidx.valloc(month=[6, 7, 8])
            array([datetime.date(2021, 6, 30), datetime.date(2021, 7, 31),
            datetime.date(2021, 8, 31), datetime.date(2022, 6, 30),
            datetime.date(2022, 7, 31), datetime.date(2022, 8, 31)],
            dtype=object)
        """
        return self.main.valloc(year, month, day)



