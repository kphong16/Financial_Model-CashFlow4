#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 21:39:20 2021

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
        self.mtrt       = 29
        self.cstrnprd   = 23
        self.idxname    = ["prjt",         "cstrn",        "loan",     "sales"]
        self.start      = ["2021-12",      "2022-01",      "2022-01",  "2022-01"]
        self.periods    = [self.mtrt+3,    self.cstrnprd,  self.mtrt,  self.mtrt]
        self.freq       = "M"
        
        self.idx = cf.PrjtIndex(idxname = self.idxname,
                                start   = self.start,
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
        self.amt_ntnl = 1_500
        self.amt_intl = 1_500
        
        self.equity = cf.Loan(self.idx,
                              amt_ntnl = self.amt_ntnl,
                              amt_intl = self.amt_intl)
        
        
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
        self.title      = ["tra",     "trb",    "trc"]
        self.rnk        = [0,         1,        2]
        self.amt_ntnl   = [57_000,    16_000,   24_000]
        self.amt_intl   = [     0,    16_000,   24_000]
        self.rate_fee   = [0.020,     0.020,    0.020]
        self.rate_IR    = [0.041,     0.065,    0.090]
        self.rate_arng  =  0.02
        
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
                                  rate_IR   = self.rate_IR)
        
        
class FncCst(object):
    def __init__(self, fnc_loan):
        self.fnc_loan = fnc_loan
        self._dct = {}
        
        self._input_initial_data()
        
    ########################################
    #### Input Data                     ####
    def _input_initial_data(self):
        #############################
        #### Financing Cost Data ####
        
        ## Arangement Fee ##
        _ipt = {"title"         : "arngfee",
                "byname"        : "주관수수료",
                "amtbase"       : self.fnc_loan.amt_ttl,
                "ratebase"      : self.fnc_loan.rate_arng,
                "scddidx"       : [idx.loan[0]]}
        self._dct["arngfee"] = _ipt
        self.arngfee = self._dct["arngfee"]
        self.arngfee["amtttl"] = self.arngfee["amtbase"] * self.arngfee["ratebase"]
        self.arngfee["scddamt"] = self.arngfee["amtttl"]
        self.arngfee["account"] = Account(idx, self.arngfee["title"])
        self.arngfee["account"].addscdd(self.arngfee["scddidx"], self.arngfee["scddamt"])
        
        ## Trust Fee ##
        _ipt = {"title"         : "trstfee",
                "byname"        : "신탁수수료",
                "amtbase"       : 125_000,
                "ratebase"      : 0.01,
                "scddidx"       : [idx.loan[0]]}
        self._dct["trstfee"] = _ipt
        self.trstfee = self._dct["trstfee"]
        self.trstfee["amtttl"] = self.trstfee["amtbase"] * self.trstfee["ratebase"]
        self.trstfee["scddamt"] = self.trstfee["amtttl"]
        self.trstfee["account"] = Account(idx, self.trstfee["title"])
        self.trstfee["account"].addscdd(self.trstfee["scddidx"], self.trstfee["scddamt"])
        
        ## Consulting Fee ##
        _ipt = {"title"         : "csltfee",
                "byname"        : "컨설팅비용",
                "csltname"      : ["jll",   "kpmg", "kyungil"],
                "amtlst"        : [40,      40,     70],
                "amtintllst"    : [10,      0,      0],
                "scddidx"       : [idx.prjt[0], idx.loan[0]]}
        self._dct["csltfee"] = _ipt
        self.csltfee = self._dct["csltfee"]
        self.csltfee["amtttl"] = sum(self.csltfee["amtlst"])
        self.csltfee["amtintl"] = sum(self.csltfee["amtintllst"])
        self.csltfee["amtrsdl"] = self.csltfee["amtttl"] - self.csltfee["amtintl"]
        self.csltfee["scddamt"] = [self.csltfee["amtintl"], self.csltfee["amtrsdl"]]
        self.csltfee["account"] = Account(idx, self.csltfee["title"])
        self.csltfee["account"].addscdd(self.csltfee["scddidx"], self.csltfee["scddamt"])
        
        ## Legal Service Fee ##
        _ipt = {"title"         : "lglfee",
                "byname"        : "법률자문수수료",
                "amtttl"        : 30,
                "scddidx"       : [idx.loan[0]]}
        self._dct["lglfee"] = _ipt
        self.lglfee = self._dct["lglfee"]
        self.lglfee["account"] = Account(idx, self.lglfee["title"])
        self.lglfee["account"].addscdd(self.lglfee["scddidx"], self.lglfee["amtttl"])
        
        ## Agent Banking Fee ##
        _ipt = {"title"         : "agntbnk",
                "byname"        : "대리금융기관",
                "scddidx"       : [idx.loan[0], idx.loan[12], idx.loan[24]],
                "amtunit"       : 30}
        self._dct["agntbnk"] = _ipt
        self.agntbnk = self._dct["agntbnk"]
        self.agntbnk["account"] = Account(idx, self.agntbnk["title"])
        self.agntbnk["account"].addscdd(self.agntbnk["scddidx"], self.agntbnk["amtunit"])
        self.agntbnk["amtttl"] = sum(self.agntbnk["account"].df["add_scdd"])
        
        ## SPC Operating Cost ##
        _ipt = {"title"         : "spcoprtg",
                "byname"        : "SPC유동화비용",
                "amtttl"        : 66,
                "scddidx"       : [idx.loan[0]]}
        self._dct["spcoprtg"] = _ipt
        self.spcoprtg = self._dct["spcoprtg"]
        self.spcoprtg["account"] = Account(idx, self.spcoprtg["title"])
        self.spcoprtg["account"].addscdd(self.spcoprtg["scddidx"], self.spcoprtg["amtttl"])
        
        
    def lfkey(self, key_name, return_val="item", dct_ipt=None):
        """
        PARAMETERS
        - key_name : key name of dictionary which is looking for
        - return_val : 
            + "item" : return items of the dictionary
            + "dict" : return the dictionary itself
        - dct : dictionary on which key is looking for
        """
        lst = []
        if dct_ipt is None:
            dct = self._dct
        else:
            dct = dct_ipt
        for key, item in dct.items():
            if key == key_name:
                if return_val == "item":
                    lst.append(item)
                elif return_val == "dict":
                    lst.append(dct)
            if type(item) == dict:
                tmp_lst = self.lfkey(key_name, return_val=return_val, dct_ipt=item)
                lst.extend(tmp_lst)
        return lst

        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        