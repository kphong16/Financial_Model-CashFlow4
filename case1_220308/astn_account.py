#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import cafle as cf
from cafle import Account

# Get attributes from main
idx = None


class Acc:
    def __init__(self):
        self._dct = {}
        self._keys = []
        
        Account._index = idx.prjt
        
        title, byname = "oprtg", "운영계좌"
        acc = self._set_account(title, byname)
        
        title, byname = "repay", "상환계좌"
        acc = self._set_account(title, byname)
        
        
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
        
        