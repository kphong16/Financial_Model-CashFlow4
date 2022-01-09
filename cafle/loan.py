#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong

LOAM

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

from .genfunc import (
    PY, 
    limited
    )
from .index import(
    Index,
    PrjtIndex
    )
from .account import (
    Account,
    Merge
    )
from .index import Index, PrjtIndex

__all__ = ['Loan', 'Merge_loan', 'Intlz_loan']

class Loan(object):
    """
    Parameters
    ----------
    index : Index, basic index class
    idxfn : Index, financial index class
    amt_ntnl : float, notional amount
    rate_IR : float, interest rate
    cycle_IR : int, interest payment cycle(months)
    title : str, name of loan
    rnk : int, rank of loan
    rate_fee : float, initial fee rate
    rate_fob : float, fee on balance which is not withdrawed
    
    Attributes
    ----------
    index : basic index class
    idxfn : financial index class
    amt_ntnl : notional amount
    rate_IR : interest rate
    cycle_IR : interest payment cycle(months)
    title : name of loan
    rnk : rank of loan
    rate_fee : initial fee rate
    rate_fob : fee on balance which is not withdrawed
    dct : dictionary of accounts(ntnl, IR, etc.)
    dctmrg : merge of dictionary
    _df : dataframe of dctmrg
    df : dataframe of dctmrg
    ntnl : account of notional amount
    IR : account of interest rate
    fee : account of fee
    fob : account of fee on balance
    is_wtdrbl : whether it is withdrawable
    is_repaid : whether it is repaid
        
    Methods
    -------
    set_wtdrbl_intldate(date, basedate=None)
    setback_wtdrbl_mtrt(date)
    set_wtdrbl_false()
    
    set_repaid(date)
    IRamt_topay(idxno) : calculate IR amount to pay
    fobamt_topay(idxno) : calculate fob amount to pay
    wtdrw(idxno, amt, acc) : withdraw amount from the notional and send to the account
    ntnl_bal_end(idxno) : notional balance that is not repayed on the index date
    amt_rpy_exptd(idxno) : notional amount which repayment date has arrived
    ntnl_out_rsdl(idxno) : residual loan notional amount that is withdrawble
    amt_repay(idxno, amt): input the amount and return the amount within notional balance end
    """
    def __init__(self,
                 title = None, # string, "LoanA"
                 index = Index('2020-01', periods=1), # basic index class
                 idxfn = None, # financial index class
                 amt_ntnl = 0, # float, notional amount
                 amt_intl = 0, # initial withdraw amount
                 rate_IR = 0.0, # float, interest rate
                 cycle_IR = 1, # int, months,
                 rnk = 0, # int, rank of loans
                 **kwargs
                 ):
        
        self.index = index
        if idxfn is None:
            self.idxfn = index
        else:
            self.idxfn = idxfn
        
        self.amt_ntnl = amt_ntnl
        self.amt_intl = amt_intl
        self.rate_IR = rate_IR
        self.cycle_IR = cycle_IR
        self.title = title
        self.rnk = rnk
        
        # Input kwargs data
        self.fnkey = []
        for key, item in kwargs.items():
            keysplit = key.split("_")
            if keysplit[0] == "rate":
                if item is not None:
                    self.fnkey.append(keysplit[1])
                    setattr(self, key, item)
            
        self._is_wtdrbl = False
        self._is_repaid = False
            
        self._dct = {}
        self._intlz()
        
        
    @property
    def dct(self):
        return self._dct
        
    @property
    def dctmrg(self):
        return Merge(self._dct)
        
    @property
    def _df(self):
        return self.dctmrg._df
        
    @property
    def df(self):
        return self.dctmrg.df
        
        
    def _intlz(self):
        for key in self.fnkey:
            setattr(self, key, Account(self.index, self.title))
        self.ntnl = Account(self.index, self.title)
        self.ntnl.amt = self.amt_ntnl
        self.ntnl.subscd(self.idxfn[0], self.ntnl.amt)
        self.ntnl.addscd(self.idxfn[-1], self.ntnl.amt)
        self._dct['ntnl'] = self.ntnl
        
        self.IR = Account(self.index, self.title)
        self.IR.rate = self.rate_IR
        self.IR.cycle = self.cycle_IR
        self.IR.rate_cycle = self.IR.rate * self.IR.cycle / 12
        self.dct['IR'] = self.IR
        
        # Fee
        if 'fee' in self.fnkey:
            self.fee = Account(self.index, self.title)
            self.fee.rate = self.rate_fee
            self.fee.amt = self.ntnl.amt * self.fee.rate
            self.dct['fee'] = self.fee
        
        # Fob
        if 'fob' in self.fnkey:
            self.fob = Account(self.index, self.title)
            self.fob.rate = self.rate_fob
            self.fob.cycle = self.cycle_IR
            self.fob.rate_cycle = self.fob.rate * self.fob.cycle / 12
            self.dct['fob'] = self.fob
            
            
    # Set loan withdrawable
    @property
    def is_wtdrbl(self):
        return self._is_wtdrbl
    @is_wtdrbl.setter
    def is_wtdrbl(self, value):
        self._is_wtdrbl = value
        
    def set_wtdrbl_intldate(self, date, basedate=None):
        """If the date is the initial date, then set is_wtdrbl True."""
        if basedate is None:
            basedate = self.idxfn[0]
        if date == basedate:
            self.is_wtdrbl = True
            
    def setback_wtdrbl_mtrt(self, date):
        """If the date is a maturity date, then set back is_wtdrbl False."""
        if date == self.idxfn[-1]:
            self.set_wtdrbl_false()
            
    def set_wtdrbl_false(self):
        """Set is_wtdrbl False"""
        self.is_wtdrbl = False
        
        
    # Set loan repaid all
    @property
    def is_repaid(self):
        return self._is_repaid
    @is_repaid.setter
    def is_repaid(self, value):
        self._is_repaid = value
    
    def set_repaid(self, date):
        if self.is_wtdrbl == False:
            return
        if -self.ntnl.bal_end[date] > 0:
            return
        if (self.ntnl.rsdl_out_cum[date] - max(self.ntnl.rsdl_in_cum[date], 0)) > 0:
            return
        self.is_repaid = True
        
        
    # Calculate IR amount to pay
    def IRamt_topay(self, idxno):
        IRamt = -self.ntnl.bal_strt[idxno] * self.IR.rate_cycle
        return IRamt
        
    def fobamt_topay(self, idxno):
        if 'fob' in self.fnkey:
            fobamt = self.ntnl_out_rsdl(idxno) * self.fob.rate_cycle
            return fobamt
        raise ValueError('fob is not created')
    
    
    # Withdraw loan
    def wtdrw(self, idxno, amt, acc):
        """Withdraw the amount to the account within the withdrawable balance limit."""
        if not self.is_wtdrbl:
            return 0
        if self.is_repaid:
            return 0
        
        amt_wtdrw = limited(amt,
                            upper = [self.ntnl.rsdl_out_cum[idxno]],
                            lower = [0])
        if amt_wtdrw > 0:
            self.ntnl.send(idxno, amt_wtdrw, acc)
        return amt_wtdrw
    
    
    # Repayment
    def ntnl_bal_end(self, idxno):
        """Notional balance that is not repayed."""
        return -self.ntnl.bal_end[idxno]
    
    def amt_rpy_exptd(self, idxno):
        """Notional amount which repayment date has arrived."""
        amt_rpy = limited(self.ntnl.rsdl_in_cum[idxno],
                          upper = [self.ntnl_bal_end(idxno)],
                          lower = [0])
        return amt_rpy
        
    def ntnl_out_rsdl(self, idxno):
        """Residual loan notional amount that is withdrawble."""
        amt_rsdl = limited(self.ntnl.rsdl_out_cum[idxno],
                           lower=[0])
        return amt_rsdl
    
    def amt_repay(self, idxno, amt):
        amtrpy = limited(amt,
                         upper = [self.ntnl_bal_end(idxno)],
                         lower = [0])
        return amtrpy
        
    def __repr__(self):
        """
        Return a string representation for this object.
        """
        repr_smry =(f"{'Title':<10}: {self.title}\n" + 
                    f"{'Notional':<10}: {self.amt_ntnl:,.0f}\n" + 
                    f"{'IR':<10}: {self.rate_IR*100:.1f}%\n"
                    )
        
        if 'fee' in self.fnkey:
            repr_tmp = f"{'Fee':<10}: {self.rate_fee:.1f}%\n"
            repr_smry += repr_tmp
        
        if 'fob' in self.fnkey:
            repr_tmp = f"{'Fob':<10}: {self.rate_fob:.1f}%\n"
            repr_smry += repr_tmp
        
        repr_smry += str(self.__class__)
        
        return repr_smry
        
        
        
class Merge_loan(Merge):
    
    """ This raises an error. 
    @property
    def _df(self):
        tmp_dct = {key:val._df for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
    
    @property
    def df(self):
        tmp_dct = {key:val.df for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
    """

    @property
    def ntnl(self):
        tmp_dct = {key:val.ntnl for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
        
    @property
    def IR(self):
        tmp_dct = {key:val.IR for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
        
    @property
    def fee(self):
        tmp_dct = {key:val.fee for key, val in self.dct.items() if 'fee' in val.fnkey}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
        
    @property
    def fob(self):
        tmp_dct = {key:val.fob for key, val in self.dct.items() if 'fob' in val.fnkey}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc    
    
    
    def __repr__(self):
        """Return a string representation for this object."""
        repr_key = []
        for key in self.dct.keys():
            repr_key.append(key)
            
        return f"Loan: {repr_key}"
    
        
class Intlz_loan:
    def __init__(self,
                 index, # basic index class
                 idxfn = None, # financial index class
                 title = [], # list, loan name
                 rnk = [], # list, loan rank
                 amt_ntnl = [], # list/float, loan notional amount
                 amt_intl = [], # list/float, loan initial withdraw amount
                 rate_IR = [], # list/float
                 cycle_IR = 1, # int or list / default 1 months
                 **kwargs
                 ):
        self.index = index
        self.idxfn = idxfn
        
        self.title = title
        self.len = len(title)
        self.rnk = rnk
        self.amt_ntnl = amt_ntnl
        self.amt_intl = amt_intl
        self.rate_IR = rate_IR
        self.cycle_IR = cycle_IR
        
        # Input kwargs data
        self.fnkey = []
        for key, item in kwargs.items():
            keysplit = key.split('_')
            if keysplit[0] == 'rate':
                self.fnkey.append(keysplit[1])
                setattr(self, key, item)
            else:
                setattr(self, key, item)
                
        self._dct = {}
        self._intlz()
        
    def __len__(self):
        return len(title)
        
    @property
    def dct(self):
        return self._dct
        
    def _intlz(self):
        for i in range(self.len):
            tmpinstnc = Loan(title = self.title[i],
                             index = self.index,
                             idxfn = self.idxfn,
                             amt_ntnl = self.amt_ntnl[i],
                             amt_intl = self.amt_intl[i],
                             rate_IR = self.rate_IR[i],
                             cycle_IR = self.cycle_IR,
                             rnk = self.rnk[i],
                             rate_fee = self.rate_fee[i] if 'fee' in self.fnkey else None,
                             rate_fob = self.rate_fob[i] if 'fob' in self.fnkey else None,
                             )
            self._dct[self.title[i]] = tmpinstnc
            setattr(self, self.title[i], tmpinstnc)
            
        self.ttl = Merge_loan(self._dct)
        for key in self.title:
            setattr(self.ttl, key, self._dct[key])
        
    def __getitem__(self, val):
        if type(val) is int:
            for key, item in self._dct.items():
                if item.rnk == val:
                    return item
        if type(val) is str:
            return getattr(self, val)
            
    def __getattr__(self, attr):
        return self.__dict__[attr]
        
    def __repr__(self):
        repr_smry = (f"{'Titles':<10}: {self.title}\n" +
                     f"{'Notional':<10}: {self.amt_ntnl}\n" +
                     f"{'IR':<10}: {self.rate_IR}\n"
                     )
                     
        if 'fee' in self.fnkey:
            repr_tmp = f"{'Fee':<10}: {self.rate_fee}\n"
            repr_smry += repr_tmp
        
        if 'fob' in self.fnkey:
            repr_tmp = f"{'Fob':<10}: {self.rate_fob}\n"
            repr_smry += repr_tmp
        
        repr_smry += str(self.__class__)
        
        return repr_smry
        
    @property
    def is_repaid(self):
        for key, item in self._dct.items():
            if item.is_repaid == False:
                return False
        return True
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
                
        