#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong

ASSUMPTION

Modules
-------


Attributes
----------


Methods
-------


"""

__all__ = ['Assumption_Base']
        
import cafle as cf
from cafle import Account

class Assumption_Base:
    def __init__(self):
        self._dct = {}
        self._dctsgmnt = {}
        self._keys = []
        self._keysgmnt = []
        
    @property
    def dct(self):
        if len(self._dct) == 0:
            return None
        return self._dct
        
    @property
    def dctsgmnt(self):
        if len(self._dctsgmnt) == 0:
            return None
        return self._dctsgmnt
        
    @property
    def keys(self):
        if len(self._keys) == 0:
            return None
        return self._keys
        
    @property
    def keysgmnt(self):
        if len(self._keysgmnt) == 0:
            return None
        return self._keysgmnt
        
    @property
    def mrg(self):
        return cf.Merge(self._dct)
        
    def _set_account(self, title, byname, sgmnt=None):
        
        _acc = Account(title=title, byname=byname)
        
        if sgmnt is not None:
            if sgmnt not in self._dctsgmnt:
                self._dctsgmnt[sgmnt] = {}
            self._keysgmnt.append(sgmnt)
            self._dctsgmnt[sgmnt][title] = _acc
            setattr(self, sgmnt, self._dctsgmnt[sgmnt])
        
        setattr(self, title, _acc)
        self._dct[title] = _acc
        self._keys.append(title)
        return _acc
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        