#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021.12.24
Golf club developing project

@author: KP_Hong
"""

import pandas as pd
from pandas import Series, DataFrame
import numpy as np

import cafle as cf
from cafle import Account
from cafle.genfunc import rounding as R
from cafle.genfunc import PY
from cafle.genfunc import EmptyClass


# Get Attributes from Main
idx = None

class Idx(object):
    def __init__(self):
        self._input_initial_data()
        
    ########################################
    #### Input Data                     ####
    def _input_initial_data(self):
        ####################
        #### Index Data ####
        self.cstrnprd   = 24
        self.mtrt       = 30
        self.fndprd     = 60
        self.prjt       = self.fndprd + 5
        self.mrtgprd    = self.prjt - 29
        self.idxname    = ["prjt",    "loan",    "fund",      "cstrn",       "mrtg",       "sales"    ]
        self.start      = ["2022-01", "2022-03", "2022-03",   "2022-05",     "2024-04",    "2024-04"  ]
        self.end        = [None,      None,      None,        None,          None,         "2027-06"  ]
        self.periods    = [self.prjt, self.mtrt, self.fndprd, self.cstrnprd, self.mrtgprd, None       ]
        self.freq       = "M"
        
        self.idx = cf.PrjtIndex(idxname = self.idxname,
                                start   = self.start,
                                end     = self.end,
                                periods = self.periods,
                                freq    = self.freq)


class Equity(object):
    def __init__(self, fnc_idx):
        self.fnc_idx = fnc_idx
        self.idx = fnc_idx.idx
        self.mtrt = fnc_idx.mtrt
        self._input_initial_data()
        
    ########################################
    #### Input Data                     ####
    def _input_initial_data(self):
        #####################
        #### Equity Data ####
        self.title = "equity"
        self.amt_ntnl = 0
        self.amt_intl = 0
        
        self.equity = cf.Loan(self.idx,
                              amt_ntnl = self.amt_ntnl,
                              amt_intl = self.amt_intl)
        
#################
#### PF LOAN ####
class Loan(object):
    def __init__(self, fnc_idx):
        self.fnc_idx = fnc_idx
        self.idx = fnc_idx.idx
        self.mtrt = fnc_idx.mtrt
        self._input_initial_data()
        
    ########################################
    #### Input Data                     ####
    def _input_initial_data(self):
        ###################
        #### Loan Data ####
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
                           
        self.loan = cf.Intlz_loan(self.idx, self.idx.loan,
                                  title     = self.title,
                                  rnk       = self.rnk,
                                  amt_ntnl  = self.amt_ntnl,
                                  amt_intl  = self.amt_intl,
                                  rate_fee  = self.rate_fee,
                                  rate_IR   = self.rate_IR,
                                  rate_fob  = self.rate_fob,
                                  amt_fee   = self.amt_fee,
                                  amt_IR    = self.amt_IR,
                                  rate_allin= self.rate_allin)
        self.loan.rate_arng     = self.rate_arng
        self.loan.amt_ttl       = self.amt_ttl
        self.loan.amt_arng      = self.amt_arng
        self.loan.allin         = self.allin

        
class FncCst_Loan(object):
    def __init__(self, fnc_loan):
        self.fnc_loan = fnc_loan
        self._dct = {}
        self._set_initial_data()

    @property
    def mrg(self):
        tmp = {key: item.acc for key, item in self._dct.items()}
        return cf.Merge(tmp)
        
    @property
    def dct(self):
        return self._dct

    ########################################
    #### Input Data                     ####
    def _set_initial_data(self):
        ## Arangement Fee ##
        cf.set_rate(self, "arngfee", "주관수수료", idx,
                    scddidx = idx.loan[0],
                    amt     = self.fnc_loan.amt_ttl,
                    rate    = self.fnc_loan.rate_arng)

        
#################
#### FUND ####
class Fund(object):
    def __init__(self, fnc_idx):
        self.fnc_idx = fnc_idx
        self.idx = fnc_idx.idx
        self.prd = fnc_idx.fndprd
        self._input_initial_data()
        
    ########################################
    #### Input Data                     ####
    def _input_initial_data(self):
        ###################
        #### Loan Data ####
        self.title      = ["cmn"]
        self.rnk        = [0]
        self.amt_ntnl   = [40_000]
        self.amt_intl   = [40_000]
        self.rate_fee   = [ 0.010] # 초기 펀드 설정비
        self.rate_IR    = [ 0.080] # 연간 기본 배당률
        self.rate_fob   = [ 0.000]
        self.rate_arng  =  0.030   # 초기 인수수수료
        
        self.amt_ttl    = sum(self.amt_ntnl)
        self.amt_fee    = [fee * amt for fee, amt in zip(self.rate_fee, self.amt_ntnl)]
        self.amt_IR     = [IR * amt for IR, amt in zip(self.rate_IR, self.amt_ntnl)]
        self.amt_arng   = self.amt_ttl * self.rate_arng
                           
        self.loan = cf.Intlz_loan(self.idx, self.idx.loan,
                                  title     = self.title,
                                  rnk       = self.rnk,
                                  amt_ntnl  = self.amt_ntnl,
                                  amt_intl  = self.amt_intl,
                                  rate_fee  = self.rate_fee,
                                  rate_IR   = self.rate_IR,
                                  rate_fob  = self.rate_fob,
                                  amt_fee   = self.amt_fee,
                                  amt_IR    = self.amt_IR,
                                  )
        self.loan.rate_arng     = self.rate_arng
        self.loan.amt_ttl       = self.amt_ttl
        self.loan.amt_arng      = self.amt_arng

        
class FncCst_Fund(object):
    def __init__(self, fnc_fnd):
        self.fnc_fnd = fnc_fnd
        self._dct = {}
        self._set_initial_data()
        
    @property
    def mrg(self):
        tmp = {key: item.acc for key, item in self._dct.items()}
        return cf.Merge(tmp)
    
    @property
    def dct(self):
        return self._dct
        
    ########################################
    #### Input Data                     ####
    def _set_initial_data(self):
        ## Arangement Fee ##
        cf.set_acc(self, "arngfee", "주관수수료", idx)
        self.arngfee.amtbase = self.fnc_fnd.amt_ttl
        self.arngfee.ratebase = self.fnc_fnd.rate_arng
        self.arngfee.amtttl = self.arngfee.amtbase * self.arngfee.ratebase
        self.arngfee.scddidx = idx.loan[0]
        self.arngfee.acc.addscdd(self.arngfee.scddidx, self.arngfee.amtttl)    
        
            
        
#################
#### MORTGAGE LOAN ####
class Mrtg(object):
    def __init__(self, fnc_idx):
        self.fnc_idx = fnc_idx
        self.idx = fnc_idx.idx
        self.mtrt = fnc_idx.mrtgprd
        self._input_initial_data()
        
    ########################################
    #### Input Data                     ####
    def _input_initial_data(self):
        ###################
        #### Loan Data ####
        self.title      = ["tra",     "trb"]
        self.rnk        = [0,         1]
        self.amt_ntnl   = [120_000,   30_000]
        self.amt_intl   = [120_000,   30_000]
        self.rate_fee   = [  0.010,    0.030]
        self.rate_IR    = [  0.045,    0.060]
        self.rate_fob   = [  0.000,    0.000]
        self.rate_arng  =  0.015
        
        self.amt_ttl    = sum(self.amt_ntnl)
        self.amt_fee    = [fee * amt for fee, amt in zip(self.rate_fee, self.amt_ntnl)]
        self.amt_IR     = [IR * amt for IR, amt in zip(self.rate_IR, self.amt_ntnl)]
        self.amt_arng   = self.amt_ttl * self.rate_arng
        
        #self.rate_allin = [fee/self.mtrt*12 + IR for fee, IR in zip(self.rate_fee, self.rate_IR)]
        #self.allin      = (sum(self.amt_IR) + (sum(self.amt_fee) + self.amt_arng) * 12 / self.mtrt)/self.amt_ttl
                           
        self.loan = cf.Intlz_loan(self.idx, self.idx.mrtg,
                                  title     = self.title,
                                  rnk       = self.rnk,
                                  amt_ntnl  = self.amt_ntnl,
                                  amt_intl  = self.amt_intl,
                                  rate_fee  = self.rate_fee,
                                  rate_IR   = self.rate_IR,
                                  rate_fob  = self.rate_fob,
                                  amt_fee   = self.amt_fee,
                                  amt_IR    = self.amt_IR,)
                                  #rate_allin= self.rate_allin)
        self.loan.rate_arng     = self.rate_arng
        self.loan.amt_ttl       = self.amt_ttl
        self.loan.amt_arng      = self.amt_arng
        #self.loan.allin         = self.allin

        
class FncCst_Mrtg(object):
    def __init__(self, fnc_loan):
        self.fnc_loan = fnc_loan
        self._dct = {}
        self._set_initial_data()

    @property
    def dct(self):
        return self._dct

    @property
    def mrg(self):
        tmp = {key: item.acc for key, item in self._dct.items()}
        return cf.Merge(tmp)

    ########################################
    #### Input Data                     ####
    def _set_initial_data(self):
        ## Arangement Fee ##
        cf.set_rate(self, "arngfee", "주관수수료", idx, 
                    scddidx = idx.mrtg[0],
                    amt     = self.fnc_loan.amt_ttl,
                    rate    = self.fnc_loan.rate_arng)
        
        
        
        
        
        
        
        
        