#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import cafle as cf
from cafle import Account
from cafle import Assumption_Base
from .astn_financing import idx


class Acc(Assumption_Base):
    def __init__(self):
        super().__init__()
        self._set_initial_data()
        
    def _set_initial_data(self):
        Account._index = idx.prjt
        
        title, byname = "oprtg", "운영계좌"
        acc = self._set_account(title, byname)
        
        title, byname = "repay", "상환계좌"
        acc = self._set_account(title, byname)
        
        
    
        
        
        
