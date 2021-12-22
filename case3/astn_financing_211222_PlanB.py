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
        self.mtrtbrg    = 6
        self.mtrt       = 29
        self.cstrnprd   = 23
        self.prjt       = self.mtrtbrg + self.mtrt + 5
        self.idxname    = ["prjt",       "brdg",      "loan",     "cstrn",        "sales"]
        self.start      = ["2021-11",    "2022-01",     "2022-04",  "2022-04",      "2022-04"]
        self.periods    = [self.prjt,  self.mtrtbrg,  self.mtrt,  self.cstrnprd,  self.mtrt]
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
        self.amt_ntnl   = [57_000,    40_000]
        self.amt_intl   = [     0,    40_000]
        self.rate_fee   = [0.020,     0.020]
        self.rate_IR    = [0.041,     0.080]
        self.rate_fob   = [0.005,     0.000]
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
                                  rate_IR   = self.rate_IR,
                                  rate_fob  = self.rate_fob,
                                  amt_fee   = self.amt_fee,
                                  amt_IR    = self.amt_IR,
                                  rate_allin= self.rate_allin)
        self.loan.rate_arng     = self.rate_arng
        self.loan.amt_ttl       = self.amt_ttl
        self.loan.amt_arng      = self.amt_arng
        self.loan.allin         = self.allin
        
        
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


        
#####################
#### BRIDGE LOAN ####
class BrgL(object):
    def __init__(self, fnc_idx):
        self.fnc_idx    = fnc_idx
        self.idx        = fnc_idx.idx
        self.mtrtbrg    = fnc_idx.mtrtbrg
        self._input_initial_data()
        
    ########################################
    #### Input Data                     ####
    def _input_initial_data(self):
        ###################
        #### Loan Data ####
        self.title      = ["tra"]
        self.rnk        = [0]
        self.amt_ntnl   = [15_500]
        self.amt_intl   = [15_500]
        self.rate_fee   = [0.005]
        self.rate_IR    = [0.045]
        self.rate_fob   = [0.000]
        self.rate_arng  =  0.005
        
        self.amt_ttl    = sum(self.amt_ntnl)
        self.amt_fee    = [fee * amt for fee, amt in zip(self.rate_fee, self.amt_ntnl)]
        self.amt_IR     = [IR * amt for IR, amt in zip(self.rate_IR, self.amt_ntnl)]
        self.amt_arng   = self.amt_ttl * self.rate_arng
        
        self.rate_allin = [fee/self.mtrtbrg*12 + IR for fee, IR in zip(self.rate_fee, self.rate_IR)]
        self.allin      = (sum(self.amt_IR) + (sum(self.amt_fee) + self.amt_arng) * 12 / self.mtrtbrg)/self.amt_ttl
                           
        self.loan = cf.Intlz_loan(self.idx, self.idx.brdg,
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
        
        
class BrgCst(object):
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
        tmpN = "brdgarng"
        _ipt = {"title"         : tmpN,
                "byname"        : "브릿지주관수수료",
                "amtbase"       : self.fnc_loan.amt_ttl,
                "ratebase"      : self.fnc_loan.rate_arng,
                "scddidx"       : [idx.brdg[0]]}
        self._dct[tmpN] = _ipt
        setattr(self, tmpN, _ipt)
        tmp = getattr(self, tmpN)
        
        tmp["amtttl"] = tmp["amtbase"] * tmp["ratebase"]
        tmp["scddamt"] = tmp["amtttl"]
        
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
                
        ## Trust Fee ##
        tmpN = "brdgtrst"
        _ipt = {"title"         : tmpN,
                "byname"        : "브릿지신탁수수료",
                "amtttl"        : 20,
                "scddidx"       : [idx.brdg[0]]}
        self._dct[tmpN] = _ipt
        setattr(self, tmpN, _ipt)
        tmp = getattr(self, tmpN)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        ## Appraisal Fee ##
        tmpN = "aprsl"
        _ipt = {"title"         : tmpN,
                "byname"        : "감정평가수수료",
                "amtttl"        : 15,
                "scddidx"       : [idx.brdg[0]]}
        self._dct[tmpN] = _ipt
        setattr(self, tmpN, _ipt)
        tmp = getattr(self, tmpN)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
                
        ## Legal Service Fee ##
        tmpN = "brglgl"
        _ipt = {"title"         : tmpN,
                "byname"        : "브릿지법률",
                "amtttl"        : 5,
                "scddidx"       : [idx.brdg[0]]}
        self._dct[tmpN] = _ipt
        setattr(self, tmpN, _ipt)
        tmp = getattr(self, tmpN)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
                
        ## Agent Banking Fee ##
        tmpN = "brgagnt"
        _ipt = {"title"         : tmpN,
                "byname"        : "브릿지대리금융",
                "amtttl"        : 10,
                "scddidx"       : [idx.brdg[0]]}
        self._dct[tmpN] = _ipt
        setattr(self, tmpN, _ipt)
        tmp = getattr(self, tmpN)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        