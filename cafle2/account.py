#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong

ACCOUNT

Modules
-------


Attributes
----------


Methods
-------


"""

import pandas as pd
import numpy as np
from pandas import Series, DataFrame

from datetime import datetime
from datetime import date
from functools import wraps

from .genfunc import *
from .index import Index, PrjtIndex

__all__ = ['Account', 'Merge',
           'set_acc', 'set_once', 'set_scd', 'set_rate']

class Account(object):
    """
    Parameters
    ----------
    index : index class
    title : str, name of account
    balstrt : int, float, default 0, start balance of account
    
    Attributes
    ----------
    cindex : index class
    index : index array
    title : str, name of account
    balstrt : start balance of account
    DFCOL : columns of the dataframe
    DFCOL_smry : summary columns of the dataframe
    JNLCOL : columns of the journal
        
    Methods
    -------
    <input data>
    addscd(index, amt) : add the amt on the 'scd_in' column of the dataframe.
    subscd(index, amt) : add the amt on the 'scd_out' column of the dataframe.
    addamt(index, amt, rcvfrm=None, note="add_amt")
        add the amt on the 'amt_in' column of the dataframe.
    subamt(index, amt, payto=None, note="sub_amt")
        add the amt on the 'amt_out' column of the dataframe.
    iptamt(index, amt, rcvfrm=None, payto=None, note=None):
        if amt is positive, apply addamt, else apply subamt.
    iptjnl(index, amt_in, amt_out, rcvfrm=None, payto=None, note=None)
        add the amt on the journal.
    
    <output data>
    df : return the summarised dataframe
    _df : return the total dataframe
    jnl : return the journal dataframe
    scd_in[slice] : return the value on the scd_in column.
    scd_in_cum[slice] : return the value on the scd_in_cum column.
    scd_out[slice] : return the value on the scd_out column.
    scd_out_cum[slice] : return the value on the scd_out_cum column.
    bal_strt[slice] : return the value on the bal_strt column.
    amt_in[slice] : return the value on the amt_in column.
    amt_in_cum[slice] : return the value on the amt_in_cum column.
    amt_out[slice] : return the value on the amt_out column.
    amt_out_cum[slice] : return the value on the amt_out_cum column.
    bal_end[slice] : return the value on the bal_end column.
    rsdl_in_cum[slice] : return the value on the rsdl_in_cum column.
    rsdl_out_cum[slice] : return the value on the rsdl_out_cum column.
    
    <etc.>
    amt_rqrd_excs(index, rqrdamt, minunit=100)
        return an additional amount compared to the account balance.
    send(index, amt, account, note=None)
        transfer the amount from this account to the opponent account.
    """
    def __init__(self,
                 index=None,
                 title=None,
                 balstrt=0
                 ):
        
        if isinstance(index, Index):
            self.cindex = index
            self.index = index.arr
        elif isinstance(index, PrjtIndex):
            self.cindex = index.main
            self.index = index.arr
            
        self.title = title
        self.balstrt = balstrt
        
        self._intlz()
        
    def _intlz(self):
        self._setdf()
        self._setjnl()
        self._set_outputfunc()
        
    # Initial Setting Function
    DFCOL = ['scd_in', 'scd_in_cum', 'scd_out', 'scd_out_cum', 
             'bal_strt', 'amt_in', 'amt_in_cum', 
             'amt_out', 'amt_out_cum', 'bal_end',
             'rsdl_in_cum', 'rsdl_out_cum']
    DFCOL_smry = ['bal_strt', 'amt_in', 'amt_out', 'bal_end']
    JNLCOL = ['amt_in', 'amt_out', 'rcvfrm', 'payto', 'note']
    
    def _setdf(self):
        # Initialize DataFrame
        self._df = DataFrame(np.zeros([len(self.index), len(self.DFCOL)]), \
                             columns = self.DFCOL, \
                             index = self.index)
        self._df.loc[self.index[0], 'bal_strt'] = self.balstrt
        
        self._cal_bal()
        
    def _setjnl(self):
        # Initialize Journal
        self._jnl = DataFrame(columns = self.JNLCOL)
        
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
        
    # Calculate Data Balance
    def _cal_bal(self):
        self._df.scd_in_cum = self._df.scd_in.cumsum()
        self._df.scd_out_cum = self._df.scd_out.cumsum()
        self._df.amt_in_cum = self._df.amt_in.cumsum()
        self._df.amt_out_cum = self._df.amt_out.cumsum()
        
        # Calculate account balance
        for i, idx in enumerate(self.index):
            if i > 0:
                self._df.loc[idx, 'bal_strt'] = self._df.loc[idxpst, 'bal_end']
            self._df.loc[idx, 'bal_end'] = self._df.loc[idx, 'bal_strt'] \
                                         + self._df.loc[idx, 'amt_in'] \
                                         - self._df.loc[idx, 'amt_out']
            idxpst = idx
            
        # Calculate the residual of scheduled amounts
        self._df.loc[:, 'rsdl_in_cum'] = self._df.loc[:, 'scd_in_cum'] \
                                       - self._df.loc[:, 'amt_in_cum']
        self._df.loc[:, 'rsdl_out_cum'] = self._df.loc[:, 'scd_out_cum'] \
                                        - self._df.loc[:, 'amt_out_cum']
                                        
    # Input Data
    @listwrapper
    def addscd(self, index, amt):
        """
        Add the amount on the 'scd_in' column of dataframe.
        
        Parameters
        ----------
        index : index, list
        amt : int, float, list
        
        Returns
        -------
        None
        """
        if isinstance(index, int): index = self.index[index]
        self._df.loc[index, 'scd_in'] += amt
        self._cal_bal()
    
    @listwrapper
    def subscd(self, index, amt):
        """
        Add the amount on the 'scd_out' column of dataframe.
        
        Parameters
        ----------
        index : index, list
        amt : int, float, list
        
        Returns
        -------
        None
        """
        if isinstance(index, int): index = self.index[index]
        self._df.loc[index, 'scd_out'] += amt
        self._cal_bal()
        
    @listwrapper
    def addamt(self, index, amt, rcvfrm=None, note="add_amt"):
        """
        Add the amount on the 'amt_in' column of dataframe.
        
        Parameters
        ----------
        index : index, list
        amt : int, float, list
        rcvfrm : str, default None
        note : str, default "add_amt"
        
        Returns
        -------
        None
        """
        if isinstance(index, int): index = self.index[index]
        if amt == 0:
            return    
        self.iptjnl(index, amt, 0, rcvfrm, None, note)
        self._df.loc[index, 'amt_in'] += amt
        self._cal_bal()
        
    @listwrapper
    def subamt(self, index, amt, payto=None, note="sub_amt"):
        """
        Add the amount on the 'amt_out' column of dataframe.
        
        Parameters
        ----------
        index : index, list
        amt : int, float, list
        payto : str, default None
        note : str, default "sub_amt"
        
        Returns
        -------
        None
        """
        if isinstance(index, int): index = self.index[index]
        if amt == 0:
            return
        self.iptjnl(index, 0, amt, None, payto, note)
        self._df.loc[index, 'amt_out'] += amt
        self._cal_bal()
        
    @listwrapper
    def iptamt(self, index, amt, rcvfrm=None, payto=None, note=None):
        """
        If the amount is positive, apply the addamt, else apply the subamt
        
        Parameters
        ----------
        index : index, list
        amt : int, float, list
        rcvfrm : str, default None
        payto : str, default None
        note : str, default "sub_amt"
        
        Returns
        -------
        None
        """
        if isinstance(index, int): index = self.index[index]
        if amt == 0:
            return
        if amt > 0:
            if rcvfrm is None:
                rcvfrm = "add_amt"
            self.addamt(index, amt, rcvfrm, note)
        else:
            if payto is None:
                payto = "sub_amt"
            self.subamt(index, -amt, payto, note)
        
    def iptjnl(self, index, amt_in, amt_out, rcvfrm=None, payto=None, note=None):
        """
        Add the amount on the journal.
        
        Parameters
        ----------
        index : index
        amt_in : int, float
        amt_out : int, float
        rcvfrm : str, default None
        payto : str, default None
        note : str, default None
        """
        if isinstance(index, int): index = self.index[index]
        tmpjnl = DataFrame([[amt_in, amt_out, rcvfrm, payto, note]], 
                           columns=self.JNLCOL, index=[index])
        self._jnl = pd.concat([self._jnl, tmpjnl])
    
    def __getattr__(self, attr):
        return self.__dict__[attr]
        
        
    # Output Data
    @property
    def df(self):
        """
        Return the summarised dataframe
        Return columns : DFCOL_smry
            ['bal_strt', 'amt_in', 'amt_out', 'bal_end']
        """
        return self._df.loc[:, self.DFCOL_smry]
    
    @property
    def jnl(self):
        """
        Return the journal dataframe
        Return columns : JNLCOL
            ['amt_in', 'amt_out', 'rcvfrm', 'payto', 'note']
        """
        return self._jnl
    
    class getattr_dfcol:
        """
        Decorator
        Get a class name and use the class name as the column of dataframe.
        """
        def __call__(self, cls):
            def init(self, spristnc):
                self.spristnc = spristnc
                self.colname = cls.__name__
            cls.__init__ = init
            
            def getitem(self, val):
                """
                If val is an integer, return the data which is in index[val].
                If val is a date, return the data which is on the date.
                If val is a string, get the date data and return the data 
                    which is on the date.
                
                Parameters
                ----------
                val: int, slice, date, date like string, 
                    ex) 0, 1:3, datetime.date(2021, 4, 30), "2021-04", "2021-04-30"
                
                Return
                ------
                data from dataframe
                Array of data from dataframe
                
                Examples
                --------
                >>> idx = Index("2021.01", "2021.12")
                >>> acc = Account(idx, "loan")
                >>> acc.addscd(idx[0], 1000)
                >>> acc.subscd(idx[5], 800)
                >>> acc.addamt(idx[1], 500, "acc_oprtg", "amount acc oprtg")
                >>> acc.scd_in[idx[3]]
                    0.0
                >>> acc.scd_in[3]
                    0.0
                >>> acc.scd_in[0:3]
                    2021-01-31    1000.0
                    2021-02-28       0.0
                    2021-03-31       0.0
                    Name: scd_in, dtype: float64
                >>> acc.scd_in[datetime.date(2021, 3, 31)]
                    0.0
                >>> acc.scd_in["2021.04"]
                    2021-04-30    0.0
                    Name: scd_in, dtype: float64
                >>> acc.scd_in["2021"]
                    2021-01-31    1000.0
                    2021-02-28       0.0
                    2021-03-31       0.0
                    2021-04-30       0.0
                    2021-05-31       0.0
                    2021-06-30       0.0
                    2021-07-31       0.0
                    2021-08-31       0.0
                    2021-09-30       0.0
                    2021-10-31       0.0
                    2021-11-30       0.0
                    Name: scd_in, dtype: float64
                """
                if isinstance(val, date):
                    return self.spristnc._df.loc[val, self.colname]
                val = self.spristnc.cindex[val]
                return self.spristnc._df.loc[val, self.colname]
            cls.__getitem__ = getitem
            
            return cls
        
    @getattr_dfcol()
    class scd_in:
        pass
    @getattr_dfcol()
    class scd_in_cum:
        pass
    @getattr_dfcol()
    class scd_out:
        pass
    @getattr_dfcol()
    class scd_out_cum:
        pass
    @getattr_dfcol()
    class bal_strt:
        pass
    @getattr_dfcol()
    class amt_in:
        pass
    @getattr_dfcol()
    class amt_in_cum:
        pass
    @getattr_dfcol()
    class amt_out:
        pass
    @getattr_dfcol()
    class amt_out_cum:
        pass
    @getattr_dfcol()
    class bal_end:
        pass
    @getattr_dfcol()
    class rsdl_in_cum:
        pass
    @getattr_dfcol()
    class rsdl_out_cum:
        pass
        
    def _set_outputfunc(self):
        self.scd_in = self.scd_in(self)
        self.scd_in_cum = self.scd_in_cum(self)
        self.scd_out = self.scd_out(self)
        self.scd_out_cum = self.scd_out_cum(self)
        self.bal_strt = self.bal_strt(self)
        self.amt_in = self.amt_in(self)
        self.amt_in_cum = self.amt_in_cum(self)
        self.amt_out = self.amt_out(self)
        self.amt_out_cum = self.amt_out_cum(self)
        self.bal_end = self.bal_end(self)
        self.rsdl_in_cum = self.rsdl_in_cum(self)
        self.rsdl_out_cum = self.rsdl_out_cum(self)
    
    def amt_rqrd_excs(self, index, rqrdamt, minunit = 100):
        """
        Calculate the additional amount required in excess of the balance.
        
        Parameters
        ----------
        index : index number
        rqrdamt : int, float, total required amount
        minunit : int, default 100, minimum adjustment unit
        
        Returns
        -------
        amt_rqrd : float
        """
        if isinstance(index, int): index = self.index[index]
        amt_rqrd = max(rqrdamt - self.bal_end[index], 0)
        amt_rqrd = round_up(amt_rqrd, -log10(minunit))
        return amt_rqrd
    
    # Account transfer
    def send(self, index, amt, account, note=None):
        """
        Transfer the amount from this account to the opponent account.
        
        Parameters
        ----------
        index : index
        amt : int, float, amount to transfer
        account : account
        note : str, default None
        
        Returns
        -------
        None
        """
        if isinstance(index, int): index = self.index[index]
        self.subamt(index, amt, account.title, note)
        account.addamt(index, amt, self.title, note)
        

class set_initial_account_decorator():
    def __call__(self, cls):
        def init(self, sprcls, title, byname=None, idx=None, crit="addscd",
                 **kwargs):
            self.sprcls = sprcls
            if "_dct" not in sprcls.__dict__:
                sprcls._dct = {}
                sprcls.dct = sprcls._dct
                
                @property
                def mrg(self):
                    return Merge(sprcls.dct)
                sprcls.mrg = mrg
            
            if title not in sprcls._dct:
                acc = Account(idx, title)
                sprcls._dct[title] = acc
                setattr(sprcls, title, acc)
                self.acc = acc
                
                acc.byname = byname
                
                self.crit = crit
                self.kwargs = kwargs
                
            for key, item in kwargs.items():
                setattr(self, key, item)
            #self.istnc = getattr(self.sprcls, title)
            self._initialize()
        cls.__init__ = init
        
        return cls

        
@set_initial_account_decorator()
class set_acc:
    """
    Set initial account. 
    Create and initiaize an account.
    
    Parameters
    ----------
    sprcls : an account on a higher level
    title : a name of the account
    byname : a second name of the account
    idx : index, default None
    crit : str, default "addscd"
    
    Returns
    -------
    
    init(self, sprcls, title, byname=None, idx=None, crit="addscd",
         **kwargs: None)
    """
    def _initialize(self):
        pass
        
@set_initial_account_decorator()
class set_once:
    """
    Set initial account. 
    Create and initiaize an account.
    Input a data(one scheduel, one amount).
    
    Parameters
    ----------
    sprcls : an account on a higher level
    title : a name of the account
    byname : a second name of the account
    idx : index, default None
    crit : str, default "addscd" or "subscd"
    scdidx : a schedule index
    amtttl : an amount to input on
    
    Returns
    -------
    
    init(self, sprcls, title, byname=None, idx=None, crit="addscd",
         **kwargs: amtttl, scdidx)
    """
    def _initialize(self):
        if self.crit == "addscd":
            self.acc.addscd(self.scdidx, self.amtttl)
        elif self.crit == "subscd":
            self.acc.subscd(self.scdidx, self.amtttl)
            
@set_initial_account_decorator()
class set_scd:
    """
    Set initial account. 
    Create and initiaize an account.
    Input a data(scheduel list, amount list).
    
    Parameters
    ----------
    sprcls : an account on a higher level
    title : a name of the account
    byname : a second name of the account
    idx : index, default None
    crit : str, default "addscd" or "subscd"
    scdidx : a schedule index list
    scdamt : an amount list to input on
    
    Returns
    -------
    
    init(self, sprcls, title, byname=None, idx=None, crit="addscd", 
         **kwargs: scdamt, scdidx)
    """
    def _initialize(self):
        if self.crit == "addscd":
            self.acc.addscd(self.scdidx, scdamt)
        elif self.crit == "subscd":
            self.acc.subscd(self.scdidx, scdamt)
        
@set_initial_account_decorator()
class set_rate:
    """
    Set initial account. 
    Create and initiaize an account.
    Input a data(scheduel list, amount list).
    
    Parameters
    ----------
    sprcls : an account on a higher level
    title : a name of the account
    byname : a second name of the account
    idx : index, default None
    crit : str, default "addscd" or "subscd"
    scdidx : a schedule index
    amt : an amount to apply a rate on
    rate : a rate to apply to an amt
    
    Returns
    -------
    init(self, sprcls, title, byname=None, idx=None, crit="addscd", 
         **kwargs: amt, rate, scdidx)
    """
    def _initialize(self):
        scdamt = self.amt * self.rate
        if self.crit == "addscd":
            self.acc.addscd(self.scdidx, scdamt)
        elif self.crit == "subscd":
            self.acc.subscd(self.scdidx, scdamt)      
        
        
class Merge(object):
    def __init__(self, dct:dict):
        self._dct = dct
        self._set_mainidx()
        self._set_outputfunc()
        
    @property
    def _df(self):
        dflst = [self._adjust_idx(item._df) for key, item in self._dct.items()]
        return sum(dflst)
        
    @property
    def df(self):
        dflst = [self._adjust_idx(item.df) for key, item in self._dct.items()]
        return sum(dflst)
        
    @property
    def dct(self):
        return self._dct
        
    @property
    def title(self):
        dfdct = Series({key: item.title for key, item in self._dct.items()})
        return dfdct
        
    def __getattr__(self, attr):
        return [item.__dict__[attr] for key, item in self._dct.items()]
        
    def _set_mainidx(self):
        mainidx = []
        for key, item in self._dct.items():
            if len(item.cindex) > len(mainidx):
                mainidx = item.cindex
        self.cindex = mainidx
        self.index = self.cindex.arr
        
    def _adjust_idx(self, tmpdf):
        if len(tmpdf.index) < len(self.cindex):
            return DataFrame(tmpdf, index=self.index).fillna(0)
        return tmpdf
        
    class getattr_dfcol:
        """
        Decorator
        Get a class name and use the class name as the column of dataframe.
        """
        def __call__(self, cls):
            def init(self, spristnc):
                self.spristnc = spristnc
                self.colname = cls.__name__
            cls.__init__ = init
            
            def getitem(self, val):
                """
                If val is an integer, return the data which is in index[val].
                If val is a date, return the data which is on the date.
                If val is a string, get the date data and return the data 
                    which is on the date.
                
                Parameters
                ----------
                val: int, slice, date, date like string, 
                    ex) 0, 1:3, datetime.date(2021, 4, 30), "2021-04", "2021-04-30"
                
                Return
                ------
                data from dataframe
                Array of data from dataframe
                
                Examples
                --------
                >>> idx = Index("2021.01", "2021.12")
                >>> acc = Account(idx, "loan")
                >>> acc.addscd(idx[0], 1000)
                >>> acc.subscd(idx[5], 800)
                >>> acc.addamt(idx[1], 500, "acc_oprtg", "amount acc oprtg")
                >>> acc.scd_in[idx[3]]
                    0.0
                >>> acc.scd_in[3]
                    0.0
                >>> acc.scd_in[0:3]
                    2021-01-31    1000.0
                    2021-02-28       0.0
                    2021-03-31       0.0
                    Name: scd_in, dtype: float64
                >>> acc.scd_in[datetime.date(2021, 3, 31)]
                    0.0
                >>> acc.scd_in["2021.04"]
                    2021-04-30    0.0
                    Name: scd_in, dtype: float64
                >>> acc.scd_in["2021"]
                    2021-01-31    1000.0
                    2021-02-28       0.0
                    2021-03-31       0.0
                    2021-04-30       0.0
                    2021-05-31       0.0
                    2021-06-30       0.0
                    2021-07-31       0.0
                    2021-08-31       0.0
                    2021-09-30       0.0
                    2021-10-31       0.0
                    2021-11-30       0.0
                    Name: scd_in, dtype: float64
                """
                if isinstance(val, date):
                    return self.spristnc._df.loc[val, self.colname]
                val = self.spristnc.cindex[val]
                return self.spristnc._df.loc[val, self.colname]
            cls.__getitem__ = getitem
            
            return cls
        
    @getattr_dfcol()
    class scd_in:
        pass
    @getattr_dfcol()
    class scd_in_cum:
        pass
    @getattr_dfcol()
    class scd_out:
        pass
    @getattr_dfcol()
    class scd_out_cum:
        pass
    @getattr_dfcol()
    class bal_strt:
        pass
    @getattr_dfcol()
    class amt_in:
        pass
    @getattr_dfcol()
    class amt_in_cum:
        pass
    @getattr_dfcol()
    class amt_out:
        pass
    @getattr_dfcol()
    class amt_out_cum:
        pass
    @getattr_dfcol()
    class bal_end:
        pass
    @getattr_dfcol()
    class rsdl_in_cum:
        pass
    @getattr_dfcol()
    class rsdl_out_cum:
        pass
        
    def _set_outputfunc(self):
        self.scd_in = self.scd_in(self)
        self.scd_in_cum = self.scd_in_cum(self)
        self.scd_out = self.scd_out(self)
        self.scd_out_cum = self.scd_out_cum(self)
        self.bal_strt = self.bal_strt(self)
        self.amt_in = self.amt_in(self)
        self.amt_in_cum = self.amt_in_cum(self)
        self.amt_out = self.amt_out(self)
        self.amt_out_cum = self.amt_out_cum(self)
        self.bal_end = self.bal_end(self)
        self.rsdl_in_cum = self.rsdl_in_cum(self)
        self.rsdl_out_cum = self.rsdl_out_cum(self)

        
        
        
        
        