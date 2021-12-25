#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021.12.24
Golf club developing project

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
        
        