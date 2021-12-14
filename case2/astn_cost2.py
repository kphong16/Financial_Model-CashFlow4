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
    
    ###################################################################################
    #### Input Data                                                                ####
    def _input_initial_data(self):
        #########################
        #### Input Land Cost ####
        self._dct["lnd"] = {}
        self.lnd = self._dct["lnd"]
        
        ## Land Purchase Cost ##
        _ipt = {"title"       : "lnd_prchs",
                "byname"      : "용지매입비",
                "amtttl"      : 14_500,
                "scddidx"     : [idx.prjt[0], idx.loan[0]],
                "scddamt"     : [1_000,       13_500]}
        self.lnd["prchs"] = _ipt
        self.prchs = self.lnd["prchs"]

        self.prchs["account"] = Account(idx, self.prchs["title"])
        self.prchs["account"].addscdd(self.prchs["scddidx"], self.prchs["scddamt"])
        
        ## Brokerage Cost ##
        _ipt = {"title"       : "lnd_brkrg",
                "byname"      : "부동산중개비용",
                "amtbase"     : self.prchs["amtttl"],
                "ratebase"    : 0.009,
                "amtintl"     : 39,
                "scddidx"     : [idx.prjt[0], idx.loan[0]]}
        self.lnd["brkrg"] = _ipt
        self.brkrg = self.lnd["brkrg"]
                      
        self.brkrg["amtttl"] = self.brkrg["amtbase"] * self.brkrg["ratebase"]
        _tmp = self.brkrg["amtttl"] - self.brkrg["amtintl"]
        self.brkrg["scddamt"] = [self.brkrg["amtintl"], _tmp]
        self.brkrg["account"] = Account(idx, self.brkrg["title"])
        self.brkrg["account"].addscdd(self.brkrg["scddidx"], self.brkrg["scddamt"])
        
        ## National Housing Bond ##
        _ipt = {"title"         : "lnd_nhbond",
                "byname"        : "국민주택채권",
                "amtbase"       : self.prchs["amtttl"],
                "매입률"          : 0.045,
                "본인부담률"       : 0.055,
                "scddidx"       : [idx.loan[0]]}
        self.lnd["nhbond"] = _ipt
        self.nhbond = self.lnd["nhbond"]
        
        self.nhbond["amtttl"] = self.nhbond["amtbase"] * self.nhbond["매입률"] * self.nhbond["본인부담률"]
        self.nhbond["scddamt"] = self.nhbond["amtttl"]
        self.nhbond["account"] = Account(idx, self.nhbond["title"])
        self.nhbond["account"].addscdd(self.nhbond["scddidx"], self.nhbond["scddamt"])

        ## Judicial Scrivener Cost ##
        _ipt = {"title"         : "lnd_jdclcst",
                "byname"        : "법무사비용",
                "amtbase"       : self.prchs["amtttl"],
                "ratebase"      : 0.001,
                "scddidx"       : [idx.loan[0]]}

        self.lnd["jdclcst"] = _ipt
        self.jdclcst = self.lnd["jdclcst"]

        self.jdclcst["amtttl"] = self.jdclcst["amtbase"] * self.jdclcst["ratebase"]
        self.jdclcst["scddamt"] = self.jdclcst["amtttl"]
        self.jdclcst["account"] = Account(idx, self.jdclcst["title"])
        self.jdclcst["account"].addscdd(self.jdclcst["scddidx"], self.jdclcst["scddamt"])

        ## Land Acquisition and Registration Tax ##
        _ipt = {"title"         : "lnd_txaqstn",
                "byname"        : "취등록세",
                "amtbase"       : self.prchs["amtttl"],
                "취득세율"        : 0.040,
                "농특세율"        : 0.002,
                "교육세율"        : 0.004,
                "scddidx"       : [idx.loan[0]]}
        self.lnd["txaqstn"] = _ipt
        self.txaqstn = self.lnd["txaqstn"]
        
        self.txaqstn["ratebase"] = self.txaqstn["취득세율"] + self.txaqstn["농특세율"] + \
                                   self.txaqstn["교육세율"]
        self.txaqstn["amtttl"] = self.txaqstn["amtbase"] * self.txaqstn["ratebase"]
        self.txaqstn["scddamt"] = self.txaqstn["amtttl"]
        self.txaqstn["account"] = Account(idx, self.txaqstn["title"])
        self.txaqstn["account"].addscdd(self.txaqstn["scddidx"], self.txaqstn["scddamt"])

        
        #################################
        #### Input Construction Cost ####
        self._dct["cstrn"] = {}
        self.cstrn = self._dct["cstrn"]
        
        ## Direct Construction Cost ##
        _ipt = {"title"         : "cstrn_ctndrt",
                "byname"        : "건축공사비",
                "amtttl"        : 65_000,
                "raterttn"      : 0.1,
                "amtintl"       : 35,
                "scddidx"       : idx.cstrn.index}
        self.cstrn["ctndrt"] = _ipt
        self.ctndrt = self.cstrn["ctndrt"]
                       
        self.ctndrt["amtprd"] = self.ctndrt["amtttl"] * (1 - self.ctndrt["raterttn"]) \
                                - self.ctndrt["amtintl"]
        self.ctndrt["amtrttn"] = self.ctndrt["amtttl"] - self.ctndrt["amtintl"] - self.ctndrt["amtprd"]
        _len = len(self.ctndrt["scddidx"])
        _unitamt = self.ctndrt["amtprd"] / _len
        self.ctndrt["account"] = Account(idx, self.ctndrt["title"])
        self.ctndrt["account"].addscdd(idx.prjt[0], self.ctndrt["amtintl"])
        self.ctndrt["account"].addscdd(self.ctndrt["scddidx"], _unitamt)
        self.ctndrt["account"].addscdd(idx.prjt[-1], self.ctndrt["amtrttn"])
        
        
        ##########################################
        #### Input Indirect Construction Cost ####
        self._dct["ctnidrt"] = {}
        self.ctnidrt = self._dct["ctnidrt"]
        
        ## License Cost ##
        _ipt = {"title"         : "ctnidrt_lcscst",
                "byname"        : "인허가비용",
                "amtttl"        : 528,
                "scddidx"       : [idx.loan[0]]}
        self.ctnidrt["lcscst"] = _ipt
        self.lcscst = self.ctnidrt["lcscst"]
        
        self.lcscst["scddamt"] = self.lcscst["amtttl"]
        self.lcscst["account"] = Account(idx, self.lcscst["title"])
        self.lcscst["account"].addscdd(self.lcscst["scddidx"], self.lcscst["scddamt"])
        
        ## Design Cost ##
        _ipt = {"title"         : "ctnidrt_dsncst",
                "byname"        : "설계비",
                "amtttl"        : 624,
                "scddidx"       : [idx.loan[0]]}
        self.ctnidrt["dsncst"] = _ipt
        self.dsncst = self.ctnidrt["dsncst"]
        
        self.dsncst["scddamt"] = self.dsncst["amtttl"]
        self.dsncst["account"] = Account(idx, self.dsncst["title"])
        self.dsncst["account"].addscdd(self.dsncst["scddidx"], self.dsncst["scddamt"])
        
        ## Supervision Cost ##
        _ipt = {"title"         : "ctnidrt_spvsn",
                "byname"        : "감리비",
                "amtttl"        : 490,
                "scddidx"       : idx.cstrn.index}
        self.ctnidrt["spvsn"] = _ipt
        self.spvsn = self.ctnidrt["spvsn"]
        
        _len = len(self.spvsn["scddidx"])
        self.spvsn["amtunit"] = self.spvsn["amtttl"] / _len
        self.spvsn["account"] = Account(idx, self.spvsn["title"])
        self.spvsn["account"].addscdd(self.spvsn["scddidx"], self.spvsn["amtunit"])
        
        ## Water suppley, Electricity etc. ##
        _ipt = {"title"         : "ctnidrt_wtrelec",
                "byname"        : "각종인입비",
                "amtttl"        : 980,
                "scddidx"       : [idx.locval(2023, 10)]}
        self.ctnidrt["wtrelec"] = _ipt
        self.wtrelec = self.ctnidrt["wtrelec"]
        
        self.wtrelec["scddamt"] = self.wtrelec["amtttl"]
        self.wtrelec["account"] = Account(idx, self.wtrelec["title"])
        self.wtrelec["account"].addscdd(self.wtrelec["scddidx"], self.wtrelec["scddamt"])
        
        ## Water and Sewage Contribution Cost ##
        _ipt = {"title"         : "ctnidrt_wsctbn",
                "byname"        : "상수도분담금",
                "amtttl"        : 163,
                "scddidx"       : [idx.locval(2023, 11)]}
        self.ctnidrt["wsctbn"] = _ipt
        self.wsctbn = self.ctnidrt["wsctbn"]
        
        self.wsctbn["scddamt"] = self.wsctbn["amtttl"]
        self.wsctbn["account"] = Account(idx, self.wsctbn["title"])
        self.wsctbn["account"].addscdd(self.wsctbn["scddidx"], self.wsctbn["scddamt"])
        
        
        ##############################
        #### Input Marketing Cost ####
        self._dct["mktg"] = {}
        self.mktg = self._dct["mktg"]

        ## Advertisement and Promotion Cost ##
        _ipt = {"title"         : "mktg_advtmt",
                "byname"        : "광고홍보비",
                "amtttl"        : 500,
                "scddidx"       : [idx.locval(2022, 6), idx.locval(2023, 6)],
                "scddrate"      : [0.5,                 0.5]}
        self.mktg["advtmt"] = _ipt
        self.advtmt = self.mktg["advtmt"]
        
        self.advtmt["scddamt"] = [self.advtmt["amtttl"] * x for x in self.advtmt["scddrate"]]
        self.advtmt["account"] = Account(idx, self.advtmt["title"])
        self.advtmt["account"].addscdd(self.advtmt["scddidx"], self.advtmt["scddamt"])
        
        ## Rent Agency Cost ##
        _ipt = {"title"         : "mktg_rntagnc",
                "byname"        : "임대대행수수료",
                "amtttl"        : 1_115,
                "scddidx"       : [idx.loan[-5]]}
        self.mktg["rntagnc"] = _ipt
        self.rntagnc = self.mktg["rntagnc"]
        
        self.rntagnc["scddamt"] = self.rntagnc["amtttl"]
        self.rntagnc["account"] = Account(idx, self.rntagnc["title"])
        self.rntagnc["account"].addscdd(self.rntagnc["scddidx"], self.rntagnc["scddamt"])
        
        ## Sales Consulting Fee ##
        _ipt = {"title"         : "mktg_slscstn",
                "byname"        : "매각컨설팅수수료",
                "amtbase"       : 125_000,
                "ratebase"      : 0.008,
                "scddidx"       : [idx.loan[0]]}
        self.mktg["slscstn"] = _ipt
        self.slscstn = self.mktg["slscstn"]
        
        self.slscstn["amtttl"] = self.slscstn["amtbase"] * self.slscstn["ratebase"]
        self.slscstn["scddamt"] = self.slscstn["amtttl"]
        self.slscstn["account"] = Account(idx, self.slscstn["title"])
        self.slscstn["account"].addscdd(self.slscstn["scddidx"], self.slscstn["scddamt"])

        
        ###############################
        #### Tax and Utility Bills ####
        self._dct["txutlt"] = {}
        self.mktg = self._dct["mktg"]
        
        
    
    #### Input Data                                                                ####
    ###################################################################################

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

        

