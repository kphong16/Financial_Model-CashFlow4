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
        acc.salesamt = 109_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.cstrn[-1], acc.salesamt)
        
    # BearLogi
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
        vltn['mngcst']  = 700
        # PM수수료 :   120원/평,월,  1,440원/평,연 <= 총괄 관리 및 관리 보고서 제출(비상근)
        # FM수수료 : 1,700원/평,월, 20,400원/평,연 <= 실제 시설관리(상근)
        # R&M    :   100원/평,월,  1,200원/평,연 <= 수선비, 장기수선충당금
        # 보험료   : 2,200원/평,월, 26,400원/평,연
        vltn['vcncy']   = 0.0
        vltn['NOI']     = (vltn['rntamt'] * (1 - vltn['vcncy'])) - vltn['mngcst']
        vltn['cap']     = 0.045
        vltn['valuation'] = vltn['NOI'] / vltn['cap'] + vltn['dpstamt']
        acc.vltn = vltn
        
        acc.salesamt = 109_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.loan[-1], acc.salesamt)

    # KBAM
    def _set_initial_data3(self):
        Account._index = idx.prjt
        
        title, byname = "sales", "자산매각대금"
        acc = self._set_account(title, byname)
        
        rnt = pd.DataFrame({
                'rntunt':[52_000, 27_000, 27_000, 27_000, 27_000],
                'mngunt':[ 3_000,  2_000,  2_000,  2_000,  2_000]},
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
        vltn['mngcst']  = 1_014
        # PM수수료 :   120원/평,월,  1,440원/평,연, 연 24백만원 <= 총괄 관리 및 관리 보고서 제출(비상근)
        # FM수수료 : 1,700원/평,월, 20,400원/평,연, 연 333백만원 <= 실제 시설관리(상근)
        # R&M    :   100원/평,월,  1,200원/평,연 <= 수선비, 장기수선충당금
        # 보험료   : 2,200원/평,월, 26,400원/평,연
        vltn['vcncy']   = 0.0
        vltn['NOI']     = (vltn['rntamt'] * (1 - vltn['vcncy'])) - vltn['mngcst']
        vltn['cap']     = 0.047
        vltn['dpstamt'] = rnt['dpstamt'].sum()
        vltn['valuation'] = vltn['NOI'] / vltn['cap'] + vltn['dpstamt']
        acc.vltn = vltn
        
        acc.salesamt = 117_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.loan[-1], acc.salesamt)
        
        
    # SeungJi
    def _set_initial_data4(self):
        Account._index = idx.prjt
        
        title, byname = "sales", "자산매각대금"
        acc = self._set_account(title, byname)
        
        rnt = pd.DataFrame({
                'rntunt':[29_000, 29_000, 29_000, 29_000, 29_000],
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
        vltn['mngcst']  = 1_014
        # PM수수료 :   120원/평,월,  1,440원/평,연 <= 총괄 관리 및 관리 보고서 제출(비상근)
        # FM수수료 : 1,700원/평,월, 20,400원/평,연 <= 실제 시설관리(상근)
        # R&M    :   100원/평,월,  1,200원/평,연 <= 수선비, 장기수선충당금
        # 보험료   : 2,200원/평,월, 26,400원/평,연
        vltn['vcncy']   = 0.0
        vltn['NOI']     = (vltn['rntamt'] * (1 - vltn['vcncy'])) - vltn['mngcst']
        vltn['cap']     = 0.044
        vltn['valuation'] = vltn['NOI'] / vltn['cap'] + vltn['dpstamt']
        acc.vltn = vltn
        
        acc.salesamt = 109_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.loan[-1], acc.salesamt)

        
        
    # KBAM2(전체상온)
    def _set_initial_data5(self):
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
        vltn['mngcst']  = 1_014
        # PM수수료 :   120원/평,월,  1,440원/평,연, 연 24백만원 <= 총괄 관리 및 관리 보고서 제출(비상근)
        # FM수수료 : 1,700원/평,월, 20,400원/평,연, 연 333백만원 <= 실제 시설관리(상근)
        # R&M    :   100원/평,월,  1,200원/평,연 <= 수선비, 장기수선충당금
        # 보험료   : 2,200원/평,월, 26,400원/평,연
        vltn['vcncy']   = 0.0
        vltn['NOI']     = (vltn['rntamt'] * (1 - vltn['vcncy'])) - vltn['mngcst']
        vltn['cap']     = 0.045
        vltn['dpstamt'] = rnt['dpstamt'].sum()
        vltn['valuation'] = vltn['NOI'] / vltn['cap'] + vltn['dpstamt']
        acc.vltn = vltn
        
        acc.salesamt = 105_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.loan[-1], acc.salesamt)
        
        
        
        
        
        