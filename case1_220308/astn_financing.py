#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import pandas as pd
from pandas import Series, DataFrame
import numpy as np

import cafle as cf
from cafle import (
    Account,
    Assumption_Base,
    )
from cafle.genfunc import (
    rounding as R,
    PY,
    EmptyClass,
    )
    

class Idx:
    def __init__(self):
        self.prd_cstrn  = 24
        self.mtrt       = 30
        self.prd_prjt   = self.mtrt + 5
        
        self.prjt   = cf.date_range("2022.01", periods=self.prd_prjt )
        self.loan   = cf.date_range("2022.03", periods=self.mtrt     )
        self.cstrn  = cf.date_range("2022.04", periods=self.prd_cstrn)
idx = Idx()
       
        
class Equity:
    def __init__(self):
        self.mtrt = idx.mtrt
        
        self.title = "equity"
        self.amt_ntnl = 0
        self.amt_intl = 0
        
        self.equity = cf.Loan(
            title       = "equity",
            index       = idx.prjt,
            amt_ntnl    = self.amt_ntnl,
            amt_intl    = self.amt_intl,
            )


class Loan:
    def __init__(self):
        self.mtrt = idx.mtrt
        
        self.title      = ["tra",     "trb"]
        self.rnk        = [0,         1]
        self.amt_ntnl   = [100_000,   30_000]
        self.amt_intl   = [ 20_000,   30_000]
        self.rate_fee   = [  0.020,    0.040]
        self.rate_IR    = [  0.050,    0.065]
        self.rate_fob   = [  0.010,    0.000]
        self.rate_arng  =  0.015
        
        self.amt_ttl    = sum(self.amt_ntnl)
        self.amt_fee    = [fee * amt for fee, amt in zip(self.rate_fee, self.amt_ntnl)]
        self.amt_IR     = [IR * amt for IR, amt in zip(self.rate_IR, self.amt_ntnl)]
        self.amt_arng   = self.amt_ttl * self.rate_arng
        
        self.rate_allin = [fee/self.mtrt*12 + IR for fee, IR in zip(self.rate_fee, self.rate_IR)]
        self.allin      = (sum(self.amt_IR) + (sum(self.amt_fee) + self.amt_arng) * 12 / self.mtrt)/self.amt_ttl
                           
        self.loan = cf.Intlz_loan(
            idx.prjt, 
            idx.loan,
            title       = self.title,
            rnk         = self.rnk,
            amt_ntnl    = self.amt_ntnl,
            amt_intl    = self.amt_intl,
            rate_fee    = self.rate_fee,
            rate_IR     = self.rate_IR,
            rate_fob    = self.rate_fob,
            amt_fee     = self.amt_fee,
            amt_IR      = self.amt_IR,
            rate_allin  = self.rate_allin,
            )
        self.loan.rate_arng     = self.rate_arng
        self.loan.amt_ttl       = self.amt_ttl
        self.loan.amt_arng      = self.amt_arng
        self.loan.allin         = self.allin
        
        
class LoanCst(Assumption_Base):
    def __init__(self, fnc_loan):
        super().__init__()
        self.fnc_loan = fnc_loan

        Account._index = idx.prjt
        
        title, byname = "arngfee", "주관수수료"
        acc = self._set_account(title, byname)
        acc.addscd(
            idxval  = idx.loan[0],
            amt     = fnc_loan.amt_ttl * fnc_loan.rate_arng,
            )
        

        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        