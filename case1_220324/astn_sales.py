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
from .astn_financing import idx, untamt
from .astn_area import area
    

class Sales(Assumption_Base):
    def __init__(self):
        super().__init__()
        self._set_initial_data2()
        
    def _set_initial_data(self):
        Account._index = idx.prjt
        
        title, byname = "sales", "자산매각대금"
        acc = self._set_account(title, byname)
        acc.salesamt = 117_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.cstrn[-1], acc.salesamt)
        
    def _set_initial_data2(self):
        Account._index = idx.prjt
        
        title, byname = "sales", "자산매각대금"
        acc = self._set_account(title, byname)
        
        rnt = pd.DataFrame({
                'rntunt':[28_000, 28_000, 28_000, 28_000, 28_000],
                'mngunt':[ 2_000,  2_000,  2_000,  2_000,  2_000]},
                index = area.rentpy.index)
        rnt['area']     = area.rentpy
        rnt['rntamt']   = rnt['area'] * rnt['rntunt'] / untamt
        rnt['mngamt']   = rnt['area'] * rnt['mngunt'] / untamt
        rnt['dpstamt']  = rnt['rntamt'] * 6
        rnt['ttlamt']   = rnt['rntamt'] + rnt['mngamt']
        rnt['rntamty']  = rnt['rntamt'] * 12
        rnt['mngamty']  = rnt['mngamt'] * 12
        rnt['ttlamty']  = rnt['ttlamt'] * 12
        acc.rnt = rnt
        
        vltn = {}
        vltn['rntamt']  = rnt['ttlamty'].sum()
        vltn['dpstamt'] = rnt['dpstamt'].sum()
        vltn['mngcst']  = 725
        vltn['NOI']     = vltn['rntamt'] - vltn['mngcst']
        vltn['cap']     = 0.045
        vltn['valuation'] = vltn['NOI'] / vltn['cap'] + vltn['dpstamt']
        acc.vltn = vltn
        
        acc.salesamt = vltn['valuation']
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.cstrn[-1], acc.salesamt)

        
        
        
        
        
        
        
        
        
        
        
        
        