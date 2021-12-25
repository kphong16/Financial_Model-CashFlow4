#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 00:56:24 2021

@author: KP_Hong
"""

import cafle as cf
from cafle import Account

# Get Attributes from Main
idx = None


class Acc(object):
    def __init__(self):
        self._dct = {}
        self._input_initial_data()
        
    ############################################
    #### Input Data                         ####
    def _input_initial_data(self):
        ## Operating Account ##
        _ipt = {"title"         : "oprtg",
                "byname"        : "운영계좌"}
        self._dct["oprtg"] = _ipt
        self.oprtg = Account(idx, self._dct["oprtg"]["title"])
        
        ## Sales Account ##
        _ipt = {"title"         : "sales",
                "byname"        : "매출계좌"}
        self._dct["sales"] = _ipt
        self.sales = Account(idx, self._dct["sales"]["title"])
        
        ## Repayment Account ##
        _ipt = {"title"         : "repay",
                "byname"        : "상환계좌"}
        self._dct["repay"] = _ipt
        self.repay = Account(idx, self._dct["repay"]["title"])
        
        ## KBAM Fund Account ##
        _ipt = {"title"         : "fund",
                "byname"        : "펀드계좌"}
        self._dct["fund"] = _ipt
        self.fund = Account(idx, self._dct["fund"]["title"])