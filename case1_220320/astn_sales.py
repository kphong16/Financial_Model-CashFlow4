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
    

class Sales(Assumption_Base):
    def __init__(self):
        super().__init__()
        self._set_initial_data()
        
    def _set_initial_data(self):
        Account._index = idx.prjt
        
        title, byname = "sales", "자산매각대금"
        acc = self._set_account(title, byname)
        acc.salesamt = 117_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.cstrn[-1], acc.salesamt)
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        