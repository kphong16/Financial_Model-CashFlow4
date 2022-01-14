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
        self.prdprjt    = 40
        self.prdfnd     = 36
        self.mtrt       = 36
        self.idxname    = ["prjt",       "loan",       "fund",    ]
        self.start      = ["2022-01",    "2022-03",    "2022-03", ]
        self.end        = [None,         None,         None,      ]
        self.periods    = [self.prdprjt, self.mtrt,    self.prdfnd]
        self.freq       = "M"
        
        self.idx = cf.PrjtIndex(idxname = self.idxname,
                                start   = self.start,
                                end     = self.end,
                                periods = self.periods,
                                freq    = self.freq)
        

class Loan(object):
    def __init__(self, cidx):
        self.cidx = cidx
        self.idx = cidx.idx
        self.mtrt = cidx.mtrt
        self._input_initial_data()
        
    def _input_initial_data(self):
        self.title      = ["tra"  ]
        self.rnk        = [0      ]
        self.amt_ntnl   = [100_000]
        self.amt_intl   = [100_000]
        self.rate_IR    = [  0.050]
        self.rate_fee   = [  0.010]
        #self.rate_fob = []
        self.rate_arng  =  0.01
        
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
                                  #rate_fob  = self.rate_fob,
                                  amt_fee   = self.amt_fee,
                                  amt_IR    = self.amt_IR,
                                  rate_allin= self.rate_allin)
        self.loan.rate_arng     = self.rate_arng
        self.loan.amt_ttl       = self.amt_ttl
        self.loan.amt_arng      = self.amt_arng
        self.loan.allin         = self.allin

        
class LoanCst(object):
    def __init__(self, cloan):
        self.cloan = cloan
        self._dct = {}
        self._set_initial_data()

    @property
    def mrg(self):
        tmp = {key: item for key, item in self._dct.items()}
        return cf.Merge(tmp)
        
    @property
    def dct(self):
        return self._dct

    def _set_initial_data(self):
        ## Arangement Fee ##
        cf.set_rate(self, "arngfee", "주관수수료", self.cloan.idx,
                    scdidx  = self.cloan.idx.loan[0],
                    amt     = self.cloan.amt_ttl,
                    rate    = self.cloan.rate_arng)

        
class Fund(object):
    def __init__(self, cidx):
        self.cidx = cidx
        self.idx = cidx.idx
        self.prd = cidx.prdfnd
        self._input_initial_data()
        
    def _input_initial_data(self):
        self.title      = ["cmn" ]
        self.rnk        = [     0]
        self.amt_ntnl   = [40_000]
        self.amt_intl   = [40_000]
        self.rate_fee   = [ 0.010] # 초기 펀드 설정비
        self.rate_IR    = [ 0.070] # 연간 기본 배당률
        #self.rate_fob   = [ 0.000]
        self.rate_arng  =  0.030   # 초기 인수수수료
        
        self.amt_ttl    = sum(self.amt_ntnl)
        self.amt_fee    = [fee * amt for fee, amt in zip(self.rate_fee, self.amt_ntnl)]
        self.amt_IR     = [IR * amt for IR, amt in zip(self.rate_IR, self.amt_ntnl)]
        self.amt_arng   = self.amt_ttl * self.rate_arng
                           
        self.fund = cf.Intlz_loan(self.idx, self.idx.fund,
                                  title     = self.title,
                                  rnk       = self.rnk,
                                  amt_ntnl  = self.amt_ntnl,
                                  amt_intl  = self.amt_intl,
                                  rate_fee  = self.rate_fee,
                                  rate_IR   = self.rate_IR,
                                  #rate_fob  = self.rate_fob,
                                  amt_fee   = self.amt_fee,
                                  amt_IR    = self.amt_IR,
                                  )
        self.fund.rate_arng     = self.rate_arng
        self.fund.amt_ttl       = self.amt_ttl
        self.fund.amt_arng      = self.amt_arng

        
class FundCst(object):
    def __init__(self, cfnd):
        self.cfnd = cfnd
        self._dct = {}
        self._set_initial_data()
        
    @property
    def mrg(self):
        tmp = {key: item for key, item in self._dct.items()}
        return cf.Merge(tmp)
    
    @property
    def dct(self):
        return self._dct
        
    ########################################
    #### Input Data                     ####
    def _set_initial_data(self):
        ## Arangement Fee ##
        cf.set_acc(self, "arngfee", "주관수수료", self.cfnd.idx)
        self.arngfee.amtbase = self.cfnd.amt_ttl
        self.arngfee.ratebase = self.cfnd.rate_arng
        self.arngfee.amtttl = self.arngfee.amtbase * self.arngfee.ratebase
        self.arngfee.scdidx = self.cfnd.idx.loan[0]
        self.arngfee.addscd(self.arngfee.scdidx, self.arngfee.amtttl)    
        
        
class Intlz(object):
    def __init__(self):
        self.dct = {}
        
        self.dct['idx'] = Idx()
        setattr(self, 'idx', self.dct['idx'].idx)
        
        self.dct['loan'] = Loan(self.dct['idx'])
        setattr(self, 'loan', self.dct['loan'].loan)
        
        self.dct['loancst'] = LoanCst(self.dct['loan'])
        setattr(self, 'loancst', self.dct['loancst'].dct)
        
        self.dct['fund'] = Fund(self.dct['idx'])
        setattr(self, 'fund', self.dct['fund'].fund)
        
        self.dct['fundcst'] = FundCst(self.dct['fund'])
        setattr(self, 'fundcst', self.dct['fundcst'].dct)
            

        