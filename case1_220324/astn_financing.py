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
    
untamt = 1_000_000

class Idx:
    def __init__(self):
        self.prd_cstrn  = 22 # 
        self.mtrt       = 28 # 28 <- BearLogi
        self.prd_prjt   = self.mtrt + 4
        
        self.prjt   = cf.date_range("2022.03", periods=self.prd_prjt )
        self.loan   = cf.date_range("2022.04", periods=self.mtrt+1   )
        self.cstrn  = cf.date_range("2022.05", periods=self.prd_cstrn)
idx = Idx()
       

class Equity:
    def __init__(self):
        self.equity = cf.Loan(
            title       = "equity",
            index       = idx.prjt,
            amt_ntnl    = 1_500,
            amt_intl    = 1_500,
            ).this
            
        self._initial_setting()
    
    def _initial_setting(self):
        self.equity.ntnl.subscd(idx.prjt[0], self.equity.amt_ntnl)


class Loan:
    def __init__(self):
        self.loan = cf.Loan(
            index       = idx.prjt,
            idxfn       = idx.loan,
            
            #Bear Logi
            rate_arng   = 0.020,
            title       = [  "tra",      "trb"],
            rnk         = [      0,          1],
            amt_ntnl    = [ 60_000,     36_000],
            amt_intl    = [      0,     36_000],
            rate_fee    = [  0.020,      0.020],
            rate_IR     = [  0.044,      0.080],
            rate_fob    = [  0.002,      0.000],
            
            #KBAM
            #rate_arng   = 0.020,
            #title       = [  "tra",      "trb"],
            #rnk         = [      0,          1],
            #amt_ntnl    = [ 58_000,     34_700],
            #amt_intl    = [      0,     34_700],
            #rate_fee    = [  0.020,      0.020],
            #rate_IR     = [  0.044,      0.080],
            #rate_fob    = [  0.002,      0.000],
            
            )
        self._initial_setting()
        
    def _initial_setting(self):
        for key, item in self.loan.dct.items():
            item.ntnl.subscd(item.idxfn[0], item.amt_ntnl)
            item.ntnl.addscd(item.idxfn[-1], item.amt_ntnl)
        
class LoanCst(Assumption_Base):
    def __init__(self, fnc_loan):
        super().__init__()
        self.fnc_loan = fnc_loan

        Account._index = idx.prjt
        
        title, byname = "arngfee", "주관수수료"
        acc = self._set_account(title, byname)
        acc.addscd(
            idxval  = idx.loan[0],
            amt     = fnc_loan.amt_arng,
            )
            
        title, byname = "brdglncst", "브릿지론비용"
        acc = self._set_account(title, byname)
        acc.addscd(idx.loan[0], 540) # 전체 540, 4월 말까지 400
            
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        