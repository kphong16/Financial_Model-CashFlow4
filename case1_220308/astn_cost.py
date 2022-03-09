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
        self._dctsgmnt = {}
        self._keys = []
        self._keysgmnt = []
        self._set_initial_data()
        
    def _set_initial_data(self):
        Account._index = idx.prjt
        
        title, byname, sgmnt = "lndprchs", "토지매입비", "lnd"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0], 52_567)
        
        title, byname, sgmnt = "levy", "분부담금", "lnd"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0], 10_802)
        
        title, byname, sgmnt = "drtcstrn", "공사비", "cstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(
            idx.cstrn,
            [70_000 / len(idx.cstrn)] * len(idx.cstrn)
            )
        title, byname, sgmnt = "adcstrn", "간접공사비", "cstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(
            idx.cstrn,
            [4_100 / len(idx.cstrn)] * len(idx.cstrn)
            )
        
        
    def _set_account(self, title, byname, sgmnt=None):
        _acc = Account(title=title, byname=byname)
        
        if sgmnt is not None:
            if sgmnt not in self._dctsgmnt:
                self._dctsgmnt[sgmnt] = {}
            self._keysgmnt.append(sgmnt)
            self._dctsgmnt[sgmnt][title] = _acc
            setattr(self, sgmnt, self._dctsgmnt[sgmnt])
            
        self._keys.append(title)
        self._dct[title] = _acc
        setattr(self, title, _acc)
        
        return _acc
        
    @property
    def dct(self):
        return self._dct
        
    @property
    def dctsgmnt(self):
        return self._dctsgmnt
        
    @property
    def keys(self):
        return self._keys
        
    @property
    def keysgmnt(self):
        return self._keysgmnt
        
    @property
    def mrg(self):
        return cf.Merge(self._dct)
        

        
        
        
        
        
        
        
        
        
        