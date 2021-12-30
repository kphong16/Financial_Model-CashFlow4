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

__all__ = ['Account']

class Account(object):
    """
    Parameters
    ----------
    
    Attributes
    ----------
    
    Methods
    -------
    
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
        if isinstance(index, int): index = self.index[index]
        self._df.loc[index, 'scd_in'] += amt
        self._cal_bal()
    
    @listwrapper
    def subscd(self, index, amt):
        if isinstance(index, int): index = self.index[index]
        self._df.loc[index, 'scd_out'] += amt
        self._cal_bal()
        
    @listwrapper
    def addamt(self, index, amt, rcvfrm=None, note="add_amt"):
        if isinstance(index, int): index = self.index[index]
        if amt == 0:
            return    
        self.iptjnl(index, amt, 0, rcvfrm, None, note)
        self._df.loc[index, 'amt_in'] += amt
        self._cal_bal()
        
    @listwrapper
    def subamt(self, index, amt, payto=None, note="sub_amt"):
        if isinstance(index, int): index = self.index[index]
        if amt == 0:
            return
        self.iptjnl(index, 0, amt, None, payto, note)
        self._df.loc[index, 'amt_out'] += amt
        self._cal_bal()
        
    @listwrapper
    def iptamt(self, index, amt, rcvfrm=None, payto=None, note=None):
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
        if isinstance(index, int): index = self.index[index]
        tmpjnl = DataFrame([[amt_in, amt_out, rcvfrm, payto, note]], 
                           columns=self.JNLCOL, index=[index])
        self._jnl = pd.concat([self._jnl, tmpjnl])
    
    def __getattr__(self, attr):
        return self.__dict__[attr]
        
        
    # Output Data
    @property
    def df(self):
        return self._df.loc[:, self.DFCOL_smry]
    
    @property
    def jnl(self):
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
                val = self.spristnc._get_idxval(val)
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
        
        
    def _get_idxval(self, val):
        if type(val) is int:
            return self.index[val]
        if type(val) is slice:
            return self.index[val]
        return val
    
    # Calculate the additional amount required in excess of the balance.
    def amt_rqrd_excs(self, index, rqrdamt, minunit = 100):
        if isinstance(index, int): index = self.index[index]
        amt_rqrd = max(rqrdamt - self.bal_end[index], 0)
        amt_rqrd = round_up(amt_rqrd, -log10(minunit))
        return amt_rqrd
    
    # Account transfer
    def send(self, index, amt, account, note=None):
        if isinstance(index, int): index = self.index[index]
        self.subamt(index, amt, account.title, note)
        account.addamt(index, amt, self.title, note)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        