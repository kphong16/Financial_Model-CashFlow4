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
idx = cf.Index(start = "2022-01", periods = 20, freq = "M")
#idx = None

class Cost(object):
    def __init__(self):
        self._dct = {}
        self._set_initial_data()
    
    ###################################################################
    #### Input Data                                                ####
    def _set_initial_data(self):
        cf.set_acc(self, "lnd", "토지비", idx)
        cf.set_once(self.lnd, "lnd", '토지비', idx, amtttl = 20000, scddidx = idx[3])
        cf.set_scdd(self.lnd, "lnd", scddidx=[idx[4], idx[5], idx[6]], 
                                   scddamt = [200, 300, 400])
        cf.set_once(self.lnd, "brkrg", "중개비", idx,
                           amtttl = 1000,
                           scddidx = idx[0])

    
    """
    class set_basic_data_decorator():
        def __call__(self, cls):
            def init(self, sprcls, title, byname=None, **kwargs):
                self.sprcls = sprcls
                if title not in sprcls._dct:
                    sprcls._dct[title] = self
                    setattr(sprcls, title, self)
                    self.title = title
                    self.byname = byname
                    self._dct = {}
                    self.acc = Account(idx, title)
                self.kwargs = kwargs
                for key, item in kwargs.items():
                    setattr(self, key, item)
                self.istc = getattr(self.sprcls, title)
                self._initialize()
            cls.__init__ = init
            return cls
    
    @set_basic_data_decorator()
    class set_acc:
        def _initialize(self):
            pass
    
    @set_basic_data_decorator()
    class set_once:
        def _initialize(self):
            self.istc.acc.addscdd(self.scddidx, self.amtttl)
    
    @set_basic_data_decorator()
    class set_scdd:
        def _initialize(self):
            self.istc.acc.addscdd(self.scddidx, self.scddamt)
    """
    
    
    
    
    
    
    
    
    
    