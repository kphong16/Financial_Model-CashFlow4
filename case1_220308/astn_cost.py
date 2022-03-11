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
from cafle import (
    Account,
    Assumption_Base,
    )
from cafle.genfunc import (
    rounding as R,
    PY,
    EmptyClass,
    )
from .astn_financing import idx
    

class Cost(Assumption_Base):
    def __init__(self):
        super().__init__()
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
        


        
        
        
        
        
        
        
        
        
        