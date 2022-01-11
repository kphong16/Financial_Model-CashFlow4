#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021.12.24
Golf club developing project

@author: KP_Hong
"""


import pandas as pd
from pandas import Series, DataFrame
import numpy as np

import cafle as cf
from cafle import Account
from cafle.genfunc import rounding as R
from cafle.genfunc import PY
from cafle.genfunc import EmptyClass

# Get Attributes from Main
idx = None

class Sales(object):
    def __init__(self):
        self._dct = {}
        self._set_initial_data()
    
    @property
    def mrg(self):
        tmp = {key: item.mrg for key, item in self._dct.items()}
        return cf.Merge(tmp)
    
    ###################################################################
    #### Input Data                                                ####
    def _set_initial_data(self):
        self.intlamt  = 12_000
        self.rateicrs = 0.015
        
        year = 0
        m = 0
        scdamt = []
        for i in idx.sales:
            yamt = self.intlamt * (1 + self.rateicrs) ** year
            mamt = yamt / 12
            scdamt.append(mamt)
            m += 1
            if m == 12:
                m = 0
                year += 1
        
        cf.set_scd(self, "sales", "운영수입", idx, "subscd",
                   scdidx = idx.sales, 
                   scdamt = scdamt)
        

        
    
    
    
    
    
    
    
    