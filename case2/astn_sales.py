#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 00:24:50 2021

@author: KP_Hong
"""

import cafle as cf
from cafle import Account

# Get Attributes from Main
idx = None


class Sales(object):
    def __init__(self):
        self._dct = {}
        self._input_initial_data()
        
    ############################################
    #### Input Data                         ####
    def _input_initial_data(self):
        ## Sales ##
        _ipt = {"title"         : "sales",
                "byname"        : "선매각대금",
                "amtttl"        : 125_000,
                "addidx"        : [idx.sales[0]],
                "scddidx"       : [idx.sales[-1]]}
        self._dct["sales"] = _ipt
        self.sales = self._dct["sales"]
        self.sales["account"] = Account(idx, self.sales["title"])
        self.sales["account"].addamt(self.sales["addidx"], self.sales["amtttl"])
        self.sales["account"].subscdd(self.sales["scddidx"], self.sales["amtttl"])
        