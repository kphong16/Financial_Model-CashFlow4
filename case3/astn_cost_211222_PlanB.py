#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 08:44:20 2021

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

class Cost(object):
    def __init__(self):
        self._dct = {}
        
        self._input_initial_data()
    
    ###################################################################
    #### Input Data                                                ####
    def _input_initial_data(self):
        #########################
        #### Input Land Cost ####
        self._dct["lnd"] = {}
        self.lnd = self._dct["lnd"]
        self.lnd["byname"] = "토지비"
        
        ## Land Purchase Cost ##
        tmpNH = "lnd"
        tmpNL = "prchs"
        _ipt = {"title"       : tmpNH+"_"+tmpNL,
                "byname"      : "용지매입비",
                "amtttl"      : 14_500,
                "scddidx"     : [idx.prjt[0],   idx.brdg[0]],
                "scddamt"     : [1_000,         13_500]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)

        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        del tmp
        
        ## Brokerage Cost ##
        tmpNH = "lnd"
        tmpNL = "brkrg"
        _ipt = {"title"       : tmpNH+"_"+tmpNL,
                "byname"      : "부동산중개비",
                "amtbase"     : self.prchs["amtttl"],
                "ratebase"    : 0.009,
                "amtintl"     : 39,
                "scddidx"     : [idx.prjt[0], idx.brdg[0]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)

        tmp["amtttl"] = tmp["amtbase"] * tmp["ratebase"]
        tmp["scddamt"] = [tmp["amtintl"], tmp["amtttl"] - tmp["amtintl"]]

        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        del tmp
        
        ## National Housing Bond ##
        tmpNH = "lnd"
        tmpNL = "nhbond"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "국민주택채권",
                "amtbase"       : self.prchs["amtttl"],
                "매입률"          : 0.045,
                "본인부담률"       : 0.055,
                "scddidx"       : [idx.brdg[0]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["amtttl"] = tmp["amtbase"] * tmp["매입률"] * tmp["본인부담률"]
        tmp["scddamt"] = tmp["amtttl"]
        
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        del tmp

        ## Judicial Scrivener Cost ##
        tmpNH = "lnd"
        tmpNL = "jdclcst"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "법무사비용",
                "amtbase"       : self.prchs["amtttl"],
                "ratebase"      : 0.001,
                "scddidx"       : [idx.brdg[0]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)

        tmp["amtttl"] = tmp["amtbase"] * tmp["ratebase"]
        tmp["scddamt"] = tmp["amtttl"]
        
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        del tmp

        ## Land Acquisition and Registration Tax ##
        tmpNH = "lnd"
        tmpNL = "txaqstn"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "취등록세",
                "amtbase"       : self.prchs["amtttl"],
                "취득세율"        : 0.040,
                "농특세율"        : 0.002,
                "교육세율"        : 0.004,
                "scddidx"       : [idx.brdg[0]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["ratebase"] = tmp["취득세율"] + tmp["농특세율"] + tmp["교육세율"]
        tmp["amtttl"] = tmp["amtbase"] * tmp["ratebase"]
        tmp["scddamt"] = tmp["amtttl"]
        
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        del tmp
        
        #################################
        #### Input Construction Cost ####
        self._dct["cstrn"] = {}
        self.cstrn = self._dct["cstrn"]
        self.cstrn["byname"] = "건축비"
        
        ## Direct Construction Cost ##
        tmpNH = "cstrn"
        tmpNL = "ctndrt"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "건축공사비",
                "amtttl"        : 65_000,
                "raterttn"      : 0.1,
                "amtintl"       : 35,
                "scddidx"       : idx.cstrn.index}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
                       
        tmp["amtprd"] = tmp["amtttl"] * (1 - tmp["raterttn"]) - tmp["amtintl"]
        tmp["amtrttn"] = tmp["amtttl"] - tmp["amtintl"] - tmp["amtprd"]
        _len = len(tmp["scddidx"])
        _unitamt = tmp["amtprd"] / _len
        
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(idx.prjt[0], tmp["amtintl"])
        tmp["account"].addscdd(tmp["scddidx"], _unitamt)
        tmp["account"].addscdd(idx.prjt[-1], tmp["amtrttn"])
        del tmp
        
        
        ##########################################
        #### Input Indirect Construction Cost ####
        self._dct["ctnidrt"] = {}
        self.ctnidrt = self._dct["ctnidrt"]
        self.ctnidrt["byname"] = "간접건축비"
        
        ## License Cost ##
        tmpNH = "ctnidrt"
        tmpNL = "lcscst"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "인허가비용",
                "amtttl"        : 528,
                "scddidx"       : [idx.loan[0]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        del tmp
        
        ## Design Cost ##
        tmpNH = "ctnidrt"
        tmpNL = "lcscst"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "설계비",
                "amtttl"        : 624,
                "scddidx"       : [idx.loan[0]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        del tmp
        
        ## Supervision Cost ##
        tmpNH = "ctnidrt"
        tmpNL = "spvsn"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "감리비",
                "amtttl"        : 490,
                "scddidx"       : idx.cstrn.index}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        _len = len(tmp["scddidx"])
        tmp["amtunit"] = tmp["amtttl"] / _len
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["amtunit"])
        
        ## Water suppley, Electricity etc. ##
        tmpNH = "ctnidrt"
        tmpNL = "wtrelec"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "각종인입비",
                "amtttl"        : 980,
                "scddidx"       : [idx.locval(2023, 10)]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        ## Water and Sewage Contribution Cost ##
        tmpNH = "ctnidrt"
        tmpNL = "wsctbn"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "상수도분담금",
                "amtttl"        : 163,
                "scddidx"       : [idx.locval(2023, 11)]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        
        ##############################
        #### Input Marketing Cost ####
        self._dct["mktg"] = {}
        self.mktg = self._dct["mktg"]
        self.mktg["byname"] = "마케팅비"

        ## Advertisement and Promotion Cost ##
        tmpNH = "mktg"
        tmpNL = "advtmt"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "광고홍보비",
                "amtttl"        : 500,
                "scddidx"       : [idx.locval(2022, 6), idx.locval(2023, 6)],
                "scddrate"      : [0.5,                 0.5]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = [tmp["amtttl"] * x for x in tmp["scddrate"]]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        ## Rent Agency Cost ##
        tmpNH = "mktg"
        tmpNL = "rntagnc"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "임대대행수수료",
                "amtttl"        : 1_115,
                "scddidx"       : [idx.loan[-2]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        ## Sales Consulting Fee ##
        tmpNH = "mktg"
        tmpNL = "slscstn"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "매각컨설팅수수료",
                "amtbase"       : 125_000,
                "ratebase"      : 0.008,
                "scddidx"       : [idx.loan[0]]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["amtttl"] = tmp["amtbase"] * tmp["ratebase"]
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])

        
        ###############################
        #### Tax and Utility Bills ####
        self._dct["txutlt"] = {}
        self.txutlt = self._dct["txutlt"]
        self.txutlt["byname"] = "제세공과금"
        
        ## Property tax ##
        tmpNH = "txutlt"
        tmpNL = "prpttx"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "재산세종부세",
                "scddidx"       : [idx.locval(2022, 6), idx.locval(2023,6)],
                "scddamt"       : [37,                  37]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["amtttl"] = sum(tmp["scddamt"])
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        ## Preservation and Registration Cost ##
        tmpNH = "txutlt"
        tmpNL = "prpttx"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "보존등기비",
                "amtbase"       : self.ctndrt["amtttl"],
                "취득세율"        : 0.028,
                "농특세율"        : 0.002,
                "교육세율"        : 0.0016,
                "법무사"          : 0.0024,
                "scddidx"       : idx.loan[-2]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["ratebase"] = tmp["취득세율"]+tmp["농특세율"]+tmp["교육세율"]+tmp["법무사"]
        tmp["amtttl"] = tmp["amtbase"] * tmp["ratebase"]
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        
        #########################
        #### Additional Cost ####
        self._dct["adtnl"] = {}
        self.adtnl = self._dct["adtnl"]
        self.adtnl["byname"] = "기타비용"
        
        ## PM Fee ##
        tmpNH = "adtnl"
        tmpNL = "pmfee"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "PM수수료",
                "amtttl"        : 200,
                "scddidx"       : idx.loan[0]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = tmp["amtttl"]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
        ## Company Operating Cost ##
        tmpNH = "adtnl"
        tmpNL = "oprtgcst"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "운영비",
                "amtunit"        : 30,
                "scddidx"       : idx.loan.index}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["amtunit"])
        tmp["amtttl"] = sum(tmp["account"].df["add_scdd"])
        
        ## Reserve Fund ##
        tmpNH = "adtnl"
        tmpNL = "rsrvfnd"
        _ipt = {"title"         : tmpNH+"_"+tmpNL,
                "byname"        : "예비비",
                "amtttl"        : 500,
                "scddidx"       : [idx.loan[10], idx.loan[20]],
                "scddrate"      : [0.5,                 0.5]}
        getattr(self, tmpNH)[tmpNL] = _ipt
        setattr(self, tmpNL, getattr(self, tmpNH)[tmpNL])
        tmp = getattr(self, tmpNL)
        
        tmp["scddamt"] = [tmp["amtttl"] * x for x in tmp["scddrate"]]
        tmp["account"] = Account(idx, tmp["title"])
        tmp["account"].addscdd(tmp["scddidx"], tmp["scddamt"])
        
    
    #### Input Data                                                ####
    ###################################################################

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

        

