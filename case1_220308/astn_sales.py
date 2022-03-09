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

class Sales:
    def __init__(self):
        self._dct = {}
        self._keys = []
        Account._index = idx.prjt
        
        title, byname = "sales", "자산매각대금"
        acc = self._set_account(title, byname)
        acc.salesamt = 1_000_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.prjt[-2], acc.salesamt)
        
        """
        self.sales = Account(
            index = idx.prjt,
            title = "sales",
            byname = "자산매각대금",
            salesamt = 1_000_000
            )
        self.sales.addamt(
            idxval  = idx.prjt[0],
            amt     = self.sales.salesamt,
            )
        self.sales.subscd(
            idxval  = idx.prjt[-2],
            amt     = self.sales.salesamt,
            )
        self._dct[self.sales.title] = self.sales
        """

        
        
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        