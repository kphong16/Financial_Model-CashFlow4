#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong
"""

import pandas as pd
import numpy as np
from pandas import Series, DataFrame

from datetime import datetime
from datetime import date
from functools import wraps

from .genfunc import (
    PY, 
    limited,
    is_scalar,
    is_iterable,
    )
from .index import(
    RangeIndex,
    DateIndex,
    date_range,
    str_to_date,
    )
from .account import (
    Account,
    Merge
    )

__all__ = ['Loan', 'Merge_loans']

class Loan(object):
    """
    Parameters
    ----------
    index       : Index, basic index class
    idxfn       : Index, financial index class
    mtrt        : int, maturity of loan
    amt_ntnl    : int or float, notional amount
    rate_IR     : float, interest rate
    rate_fee    : float, initial fee rate
    rate_fob    : float, fee on balance which is not withdrawed
    rate_arng   : float, arangement fee rate
    cycle_IR    : int, interest payment cycle(months), 1 is default
    title       : str, name of loan
    byname      : str, byname of loan
    rnk         : int, rank of loan
    **kwargs    : others
    
    Class Attributes
    ----------------
    dct         : dictionary of loans
    index       : basic index class
    idxfn       : financial index class
    mtrt        : maturity of loan
    rate_arng   : arangement fee rate
    ttl_ntnl    : total amount of notional amounts
    ttl_intl    : total amount of initial amounts
    amt_arng    : amount of arangement fee
    cycle_IR    : interest payment cycle(months), 1 is default
    
    Class Methods
    -------------
    rnk(reverse=False)  : return sorted list of rank
    is_repaid_all()     : return boolean whether loans are repaid or not
    mrgloans()          : return merge of loans
    by_rnk(rnk)         : find loan by rnk
    allin_ttl()         : total all-in rate
    
    Instance Attributes
    -------------------
    dct_item    : dictionary of loan items(ntnl, IR, etc.)
    mrgitems    : merge of item dictionary
    _df         : dataframe of mrgitems
    df          : dataframe of mrgitems
    index       : basic index class
    idxfn       : financial index class
    mtrt        : maturity of loan
    
    amt_ntnl    : notional amount
    amt_intl    : initial amount
    rate_IR     : interest rate
    rate_fee    : initial fee rate
    rate_fob    : fee on balance which is not withdrawed
    
    title       : name of loan
    byname      : byname of loan
    rnk         : rank of loan
    ntnl        : account of notional amount
    
    IR          : account of interest rate
    IR.rate     : interest rate
    IR.cycle    : interest payment cycle(months), 1 is default
    IR.rate_cycle : interest rate on a cycle
    IR.amt_year : interest rate amount on a year
    IR.amt_cycle  : interest rate amount on a cycle
    
    fee         : account of fee
    fee.rate    : initial fee rate
    fee.amt     : fee amount
    fob         : account of fee on balance
    fob.rate    : fob rate
    fob.cycle   : cycle of fob
    fob.rate_cycle : rate of fob on cycle
    is_wtdrbl   : whether it is withdrawable
    is_repaid   : whether it is repaid
    
    Instance Methods
    ----------------
    set_wtdrbl_intldate(date, basedate=None)
    setback_wtdrbl_mtrt(date)
    set_wtdrbl_false()
    set_repaid(date)
    IRamt_topay(idxno)      : calculate IR amount to pay
    fobamt_topay(idxno)     : calculate fob amount to pay
    wtdrw(idxno, amt, acc)  : withdraw amount from the notional and send to the account
    ntnl_bal_end(idxno)     : notional balance that is not repayed on the index date
    amt_rpy_exptd(idxno)    : notional amount which repayment date has arrived
    ntnl_out_rsdl(idxno)    : residual loan notional amount that is withdrawble
    amt_repay(idxno, amt)   : input the amount and return the amount within notional balance end
    """
    
    def __new__(cls, *args,**kwargs):
        cls.key_all = [key for key in kwargs.keys()]
        cls.key_essential = ['index', 'idxfn', 'mtrt', 'amt_ntnl', 'rate_IR']
        cls.key_optional = []
        cls.dct = {}
        cls._rnk = []
        cls.cycle_IR = 1
        cls.no_loan_dev = 0
        
        # Triple new
        if len(args) == 3:
            if isinstance(args[0], DateIndex):
                cls.index = args[0]
                cls.idxfn = cls.index
                cls.mtrt = len(args[0])
            elif isinstance(args[0], int):
                cls.mtrt = args[0]
                cls.index = RangeIndex(args[0])
                cls.idxfn = cls.index
                
            if isinstance(args[1], (int, float)):
                amt_ntnl = args[1]
            else:
                raise ValueError("amt_ntnl should be int or float.")
            
            if isinstance(args[2], float):
                rate_IR     = args[2]
            else:
                raise ValueError("rate_IR should be float")

            kwargs = {key: item for key, item in kwargs.items() if key not in cls.key_essential}
            
            return cls._triple_new(amt_ntnl, rate_IR, **kwargs)
            
        # Keyward arguments
        if len(args) == 0:
            for key, item in kwargs.items():
                setattr(cls, key, item)
            return cls._kwargs_new(**kwargs)
            
            
    @classmethod
    def _triple_new(cls, amt_ntnl, rate_IR, **kwargs):
        
        data = {
            'index'     : cls.index,
            'idxfn'     : cls.idxfn,
            'mtrt'      : cls.mtrt,
            'amt_ntnl'  : amt_ntnl,
            'rate_IR'   : rate_IR,
        }
        data.update(kwargs)
        result_one_val = cls._onevalue_kwargs_new(**data)
        cls._after_calculation()
        cls.this = result_one_val
        return cls

    
    @classmethod
    def _kwargs_new(cls, **kwargs):        
        if 'index' in kwargs:
            cls.index = kwargs.pop('index')
            if 'idxfn' in kwargs:
                cls.idxfn = kwargs.pop('idxfn')
            else:
                cls.idxfn = cls.index
            if 'mtrt' in kwargs:
                cls.mtrt = kwargs.pop('mtrt')
            else:
                cls.mtrt = len(cls.idxfn)
        if 'mtrt' in kwargs:
            cls.mtrt = kwargs.pop('mtrt')
            cls.index = RangeIndex(cls.mtrt)
            cls.idxfn = cls.index
        if 'rate_arng' in kwargs:
            cls.rate_arng = kwargs.pop('rate_arng')
        
        try:
            amt_ntnl = kwargs['amt_ntnl']
        except:
            ValueError("'amt_ntnl' is essential")
        
        if is_iterable(amt_ntnl):
            cls.number_of_loans = len(amt_ntnl)
            
            for no, _amt_ntnl in enumerate(amt_ntnl):
                data = {key: item[no] for key, item in kwargs.items()}
                cls._onevalue_kwargs_new(**data)
                
            cls._after_calculation()
            return cls
            
        elif not is_iterable(amt_ntnl):
            cls.number_of_loans = 1
            
            data = kwargs.copy()
            result_one_val = cls._onevalue_kwargs_new(**data)
            cls._after_calculation()
            cls.this = result_one_val
            return cls
    
    @classmethod
    def _after_calculation(cls):
        cls.ttl_ntnl = sum([item.amt_ntnl for item in cls.dct.values()])
        if 'amt_intl' in cls.key_all:
            cls.ttl_intl = sum([item.amt_intl for item in cls.dct.values()])
        if 'rate_arng' in cls.key_all:
            cls.amt_arng = cls.rate_arng * cls.ttl_ntnl
    
    @classmethod
    def _onevalue_kwargs_new(cls, **data):
        result = object.__new__(cls)
        result.dct_item = {}
        
        result.index = cls.index
        result.idxfn = cls.idxfn
        result.mtrt = cls.mtrt
        
        result._is_wtdrbl = False
        result._is_repaid = False
        
        # Rank
        if 'rnk' in data:
            result.rnk = data.pop('rnk')
        else:
            result.rnk = 0
        cls._rnk.append(result.rnk)
        
        # Notional amount
        try:
            amt_ntnl = data.pop('amt_ntnl')
        except:
            ValueError("'amt_ntnl' is essential")
        
        if 'amt_intl' in data:
            amt_intl = data['amt_intl']
        else:
            amt_intl = amt_ntnl
            
        _ntnl = Account(cls.index)
        #_ntnl.subscd(cls.idxfn[0], amt_intl)
        #_ntnl.addscd(cls.idxfn[-1], amt_ntnl)
        result.amt_ntnl = amt_ntnl
        result.amt_intl = amt_intl
        result.ntnl = _ntnl
        result.dct_item['ntnl'] = _ntnl
        
        # Interest rate
        if 'rate_IR' in data:
            rate_IR = data.pop('rate_IR')
            if 'cycle_IR' in data:
                cls.cycle_IR = data.pop('cycle_IR')

            _IR = Account(cls.index)
            _IR.rate = rate_IR
            _IR.cycle = cls.cycle_IR
            _IR.rate_cycle = rate_IR * cls.cycle_IR / 12
            _IR.amt_year = rate_IR * amt_ntnl
            _IR.amt_cycle = _IR.rate_cycle * amt_ntnl
            result.rate_IR = rate_IR
            result.IR = _IR
            result.dct_item['IR'] = _IR
        
        # Fee
        if 'rate_fee' in data:
            rate_fee = data.pop('rate_fee')
            
            _fee = Account(cls.index)
            _fee.rate = rate_fee
            _fee.amt = rate_fee * amt_ntnl
            result.rate_fee = rate_fee
            result.fee = _fee
            result.dct_item['fee'] = _fee
            
        # Fob(Fee on balance)
        if 'rate_fob' in data:
            rate_fob = data.pop('rate_fob')
            
            _fob = Account(cls.index)
            _fob.rate = rate_fob
            _fob.cycle = cls.cycle_IR
            _fob.rate_cycle = rate_fob * cls.cycle_IR / 12
            result.rate_fob = rate_fob
            result.fob = _fob
            result.dct_item['fob'] = _fob
            
        # Allin
        cst_year = 0
        if 'rate_IR' in cls.key_all:
            cst_year += amt_ntnl * rate_IR
        if 'rate_fee' in cls.key_all:
            cst_year += amt_ntnl * rate_fee / cls.mtrt * 12
        if amt_ntnl == 0 or amt_ntnl is None:
            result.allin = 0
        else:
            result.allin = cst_year / amt_ntnl
        
        # Others
        if 'title' in data:
            title = data.pop('title')
            result.title = title
        else:
            title = f"tr{cls.no_loan_dev}"
            cls.no_loan_dev += 1
            result.title = title
        
        if 'byname' in data:
            byname = data.pop('byname')
            result.byname = byname
            
        for key, item in data.items():
            setattr(result, key, item)
            
        cls.dct[title] = result
        setattr(cls, title, result)
        return result
    

    @classmethod
    def rnk(cls, reverse=False):
        if reverse == False:
            return sorted(cls._rnk, reverse=reverse)
        elif reverse == True:
            return sorted(cls._rnk, reverse=reverse)
            
    @classmethod
    def is_repaid_all(cls):
        for key, item in cls.dct.items():
            if item.is_repaid == False:
                return False
        return True
        
    @classmethod
    def mrgloans(cls):
        return Merge_loans(cls.dct)
        
    @classmethod
    def by_rnk(cls, rnk):
        for key, item in cls.dct.items():
            if item.rnk == rnk:
                return item
                
    @classmethod
    def allin_ttl(cls):
        tmpamt = 0
        for key, item in cls.dct.items():
            tmpamt += item.allin * item.amt_ntnl
        return tmpamt / cls.ttl_ntnl
        
    @property   
    def mrgitems(self):
        return Merge(self.dct_item)
            
    @property
    def _df(self):
        return self.mrgitems._df
        
    @property
    def df(self):
        return self.mrgitems.df
    
    # Set loan withdrawable
    @property
    def is_wtdrbl(self):
        return self._is_wtdrbl
    @is_wtdrbl.setter
    def is_wtdrbl(self, value):
        self._is_wtdrbl = value
        
    @property
    def keys(self):
        return list(self.__dict__.keys())
        
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
        if 'rate_fob' in self.key_all:
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
                    f"{'Notional':<10}: {self.amt_ntnl:,.0f}\n"
                    )
        if 'IR' in self.__dict__:
            repr_tmp = f"{'IR':<10}: {self.rate_IR*100:.1f}%\n"
            repr_smry += repr_tmp
        
        if 'fee' in self.__dict__:
            repr_tmp = f"{'Fee':<10}: {self.rate_fee:.1f}%\n"
            repr_smry += repr_tmp
        
        if 'fob' in self.__dict__:
            repr_tmp = f"{'Fob':<10}: {self.rate_fob:.1f}%\n"
            repr_smry += repr_tmp
        
        repr_smry += str(self.__class__)
        
        return repr_smry
        
        
class Merge_loans(Merge):
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
        tmp_dct = {key:val.fee for key, val in self.dct.items() if 'fee' in val.__dict__.keys()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
        
    @property
    def fob(self):
        tmp_dct = {key:val.fob for key, val in self.dct.items() if 'fob' in val.__dict__.keys()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc    
    
    
    def __repr__(self):
        """Return a string representation for this object."""
        repr_key = []
        for key in self.dct.keys():
            repr_key.append(key)
            
        return f"Merge_of_Loans: {repr_key}"
                
        