import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd
from datetime import datetime
from datetime import timedelta
from datetime import date
from functools import wraps

# import genfunc
from . import genfunc

__all__ = ['Index', 'PrjtIndex', 'booleanloc']

class Index(object):
    """
    PARAMETERS
    - start: day, ex) '2021-01', '2021-01-01'
    - end: day, ex) '2021-01', '2021-01-01'
    - periods: int, ex) 12 <- for twelve months
    - freq: str, ex) 'M' <- for last date of month
      + 'D' : Day
      + 'B' : Business Day
      + 'M' : MonthEnd
      + 'BM' : Business MonthEnd
      + 'MS' : MonthBegin
      + 'BMS' : Business MonthBegin
      + 'WOM-1MON', 'WOM-2MON', ... : Week of Month(1st monday of every month)
    ATTRIBUTES
    - _range : DatetimeIndex of data
    - _idxno : Index numbering
    - index : date of DatetimeIndex
    - year : year array of DatetimeIndex
    - month : month array of DatetimeIndex
    - day : day array of DatetimeIndex
    - idxno : Index numbering
    METHODS
    - __getitem__(no) : use like Index[no], return Index.index[no]
    - __len__() : use like len(Index), return len(index)
    - idxloc(year=None, month=None, day=None) :
      + Return boolean array of data(year, month, day) which is in array
    """
    def __init__(self,
                start: Day = None,
                end: Day = None,
                periods: int = None,
                freq: str = None
                ) -> None:
        self.start = start
        self.end = end
        self.periods = periods
        self.freq = freq
        self._range = pd.date_range(self.start, self.end, self.periods,
                      self.freq)
        self._idxno = np.arange(len(self._range))
        
    def __getitem__(self, no):
        return self.index[no]
        
    def __len__(self):
        return len(self.index)
        
    @property
    def index(self):
        return self._range.date
        
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
        
    def idxloc(self, year=None, month=None, day=None):
        """
        Return boolean array of data(year, month, day) is in array
        """
        isyear = _getblnloc(self.year, year)
        ismonth = _getblnloc(self.month, month)
        isday = _getblnloc(self.day, day)
        
        return isyear & ismonth & isday

    def locno(self, year, month=None, day=None):
        """
        Return index no. which data(year, month, day) is in
        """
        if isinstance(year, int):
            tmp_loc = self.idxloc(year, month, day)
        elif isinstance(year, date):
            tmp_loc = self.index == year
        
        try:
            tmpval = self.idxno[tmp_loc]
            if len(tmpval) == 1:
                return int(tmpval)
            else:
                raise ValueError
        except AttributeError as err:
            print("AttributeError", err)
            
    def locval(self, year=None, month=None, day=None):
        """
        Return index val. which data(year, month, day) is in
        """
        tmpno = self.locno(year, month, day)
        return self[tmpno]


class PrjtIndex(object):
    """
    PARAMETERS
    - idxname : list of string, ex) ['prjt', 'cstrn', 'loan', 'sales']
    - start : list of date, ex) ['2021-08', '2021-10', '2021-10', '2021-11']
    - end : list of date
    - periods : list of integer, ex) [24+1, 18+1, 20+1, 16+1]
    - freq : string, frequency of data, ex) 'M'
    - prjtno : int, default 0
      + set main, project index
      + If is is 0 then idxname[0], i.e. 'prjt' index become main and project idx
    ATTRIBUTES
    - index : date of DatetimeIndex on project index
    - year : year array of DatetimeIndex on project index
    - month : month array of DatetimeIndex on project index
    - day : day array of DatetimeIndex on project index
    - idxno : Index numbering on project index
    METHODS
    - __getitem__(no) : use like Index[no], return index[no] of project index
    - __len__() : use like len(Index), return len of project index
    - idxloc(year=None, month=None, day=None) :
      + Return boolean array of data(year, month, day) which is in array
      + Data of project index
    """
    def __init__(self, 
                 idxname,
                 start = None, 
                 end = None,
                 periods = None, 
                 freq: str = None,
                 prjtno = 0
                 ):
        self.idxname = idxname
        self.start = start
        self.end = end
        self.periods = periods
        self.freq = freq
        self._prjtno = prjtno
        
        # Initialize
        self._intlz()
        
    def _intlz(self):
        self._setidxcls()
        self._prjt = getattr(self, self.idxname[self._prjtno])
        # Set project idx to PrjtIndex._prjt
    
    def _setidxcls(self):
        """Set each index of idxname list.
        Set attributes with each idxname, for Index instance of each idxname
        """
        for no, name in enumerate(self.idxname):
            tmpidx = Index(self._isnone(self.start, no), 
                           self._isnone(self.end, no), 
                           self._isnone(self.periods, no),
                           self.freq)
            setattr(self, name, tmpidx)
    
    def _isnone(self, val, no):
        """If val is None, return None.
        If val has a data excepting None, return val[no]
        """
        if val:
            return val[no]
        else:
            return val
    
    def __getitem__(self, idxno):
        return self._prjt[idxno]
    
    def __len__(self):
        return len(self._prjt)
        
    @property
    def index(self):
        return self._prjt.index        
    
    @property
    def year(self):
        return self._prjt.year
        
    @property
    def month(self):
        return self._prjt.month
        
    @property
    def day(self):
        return self._prjt.day
        
    @property
    def idxno(self):
        return self._prjt.idxno
        
    def idxloc(self, year=None, month=None, day=None):
        return self._prjt.idxloc(year, month, day)

    def locno(self, year, month=None, day=None):
        return self._prjt.locno(year, month, day)
        
    def locval(self, year=None, month=None, day=None):
        return self._prjt.locval(year, month, day)
        
def _getblnloc(array, val):
    if val == None:
        return [True]
    else:
        return booleanloc(array)[val]


class booleanloc():
    """
    Return boolean array of data is in array
    
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
        if genfunc.is_iterable(data):
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
        
        
        