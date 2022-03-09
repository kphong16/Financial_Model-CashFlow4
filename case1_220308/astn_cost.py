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
from cafle import Account
from cafle.genfunc import (
    rounding as R,
    PY,
    EmptyClass,
    )
    
# Get attributes from main
idx = None

class Cost:
    def __init__(self):
        self._dct = {}
        self._keys = []
        self._set_initial_data()
        
    def _set_initial_data(self):
        Account._index = idx.prjt
        
        title, byname = "lnd", "토지비"
        acc = self._set_account(title, byname)
        acc.addscd(idx.loan[0], 52_567)
        
        title, byname = "levy", "분부담금"
        acc = self._set_account(title, byname)
        acc.addscd(idx.loan[0], 10_802)
        
        title, byname = "cstrn", "공사비"
        acc = self._set_account(title, byname)
        acc.addscd(
            idx.cstrn,
            [70_000 / len(idx.cstrn)] * len(idx.cstrn)
            )
        title, byname = "adcstrn", "간접공사비"
        acc = self._set_account(title, byname)
        acc.addscd(
            idx.cstrn,
            [4_100 / len(idx.cstrn)] * len(idx.cstrn)
            )
        
        
    def _set_account(self, title, byname):
        setattr(self, title, Account(title=title, byname=byname))
        acc = getattr(self, title)
        self._dct[title] = acc
        self._keys.append(title)
        return acc
        
    @property
    def dct(self):
        return self._dct
        
    @property
    def keys(self):
        return self._keys
        
    @property
    def mrg(self):
        return cf.Merge(self._dct)
        

        
        
        
        
        
        
        
        
        
        