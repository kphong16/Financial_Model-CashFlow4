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

class Cost(object):
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
        #########################
        #### Input Land Costs ####
        cf.set_acc(self, "lnd", "토지비", idx)
        cf.set_once(self.lnd, "lnd", "토지비", idx, amtttl=52_567, scddidx=idx.loan[0])
        
        #########################
        #### Input Levy Costs ####
        cf.set_acc(self, "levy", "분부담금", idx)
        cf.set_once(self.levy, "levy", "분부담금", idx, amtttl=10_802, scddidx=idx.loan[0])
        
        #########################
        #### Input Construction Costs ####
        cf.set_acc(self, "cstrn", "공사비", idx)
        cf.set_scdd(self.cstrn, "cstrn", "공사비", idx, 
                    scddamt=[70_000/len(idx.cstrn)]*len(idx.cstrn), 
                    scddidx=idx.cstrn.index)
        
        #########################
        #### Input Additional Construction Costs ####
        cf.set_acc(self, "adtlcstn", "간접공사비", idx)
        cf.set_scdd(self.adtlcstn, "adtlcstn", "간접공사비", idx, 
                    scddamt=[4_100/len(idx.cstrn)]*len(idx.cstrn), 
                    scddidx=idx.cstrn.index)
        
        #########################
        #### Input Additional Costs ####
        cf.set_acc(self, "adtnl", "기타사업비", idx)
        cf.set_scdd(self.adtnl, "adtnl", "기타사업비", idx, 
                    scddamt=[7_551/len(idx.cstrn)]*len(idx.cstrn), 
                    scddidx=idx.cstrn.index)
                    
        #########################
        #### Input Equipment Costs ####
        cf.set_acc(self, "eqmnt", "장비구입비", idx)
        cf.set_once(self.eqmnt, "eqmnt", "장비구입비", idx, amtttl=1_454, scddidx=idx.cstrn[-1])
        
        #########################
        #### Input Tax Costs ####
        cf.set_acc(self, "tax", "제세금", idx)
        cf.set_once(self.tax, "tax", "제세금", idx, amtttl=6_889, scddidx=idx.cstrn[-1])
                
            
