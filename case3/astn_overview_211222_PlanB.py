#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 10:23:26 2021

@author: KP_Hong
"""

import pandas as pd
from pandas import Series, DataFrame
import numpy as np

import cafle as cf
from cafle.genfunc import rounding as R
from cafle.genfunc import PY


class Area(object):
    def __init__(self):
        self._input_businessoverview()
        self._input_areadata()
        self._sorting_data()
        self._pivot_m2()
        self._pivot_py()
        
    def _input_businessoverview(self):
        self.bsns = {'주소': '세종특별시 부강면 문곡리 110번지',
                    '대지면적'       : cf.Area(29_998),
                    '건축면적'       : cf.Area(13_217),
                    '연면적'        : cf.Area(53_975),
                    '용적률연면적'    : cf.Area(33_213)}
    
    def _input_areadata(self):
        #### Input Area Data ####
        """
        nmlstrg : normal storage
        cldstrg : cold storage
        mchnrm : machine room
        exclsv : exclusive use space(전용면적)
        common : common use space(공용면적)
        ttlfloor : total floor(연면적)
        nonfloor : not included in total floor(연면적 미포함 면적)
        """
        self.tmp_col = ['name',    'byname', 'floor', 'exclsv', 'ttlfloor', 'area_m2']
        self.tmp_ary =[['cldstrg', '저온창고',   'b1', 'exclsv', 'ttlfloor', 8_481.27],
                       ['office',  '사무실',    'b1', 'exclsv', 'ttlfloor', 685.55],
                       ['canopy',  '캐노피',    'b1', 'exclsv', 'ttlfloor', 0.00],
                       ['stair',   '계단실',    'b1', 'exclsv', 'ttlfloor', 197.61],
                       ['berth',   'Berth',    'b1', 'exclsv', 'ttlfloor', 1_610.59],
                       ['mchnrm',  '기계실',    'b1', 'exclsv', 'ttlfloor', 1_731.67],
                       ['passage', '상하차통로', 'b1', 'common', 'ttlfloor', 2_302.99],
                       ['ramp',    '램프',      'b1', 'common', 'ttlfloor', 0.00],
                       ['cldstrg', '저온창고',   'f1', 'exclsv', 'ttlfloor', 9_526.66],
                       ['office',  '사무실',    'f1', 'exclsv', 'ttlfloor', 289.05],
                       ['canopy',  '캐노피',    'f1', 'exclsv', 'ttlfloor', 0.00],
                       ['stair',   '계단실',    'f1', 'exclsv', 'ttlfloor', 219.51],
                       ['berth',   'Berth',    'f1', 'exclsv', 'nonfloor', 870.96],
                       ['mchnrm',  '기계실',    'f1', 'exclsv', 'ttlfloor', 0.00],
                       ['passage', '상하차통로', 'f1', 'common', 'nonfloor', 1_737.88],
                       ['ramp',    '램프',      'f1', 'common', 'ttlfloor', 0.00],
                       ['nmlstrg', '상온창고',   'f2', 'exclsv', 'ttlfloor', 8_665.99],
                       ['office',  '사무실',    'f2', 'exclsv', 'ttlfloor', 243.80],
                       ['canopy',  '캐노피',    'f2', 'exclsv', 'ttlfloor', 0.00],
                       ['stair',   '계단실',    'f2', 'exclsv', 'ttlfloor', 241.00],
                       ['berth',   'Berth',    'f2', 'exclsv', 'ttlfloor', 1_576.62],
                       ['mchnrm',  '기계실',    'f2', 'exclsv', 'ttlfloor', 0.00],
                       ['passage', '상하차통로', 'f2', 'common', 'ttlfloor', 2_213.74],
                       ['ramp',    '램프',      'f2', 'common', 'ttlfloor', 0.00],
                       ['nmlstrg', '상온창고',   'f3', 'exclsv', 'ttlfloor', 8_920.76],
                       ['office',  '사무실',    'f3', 'exclsv', 'ttlfloor', 75.77],
                       ['canopy',  '캐노피',    'f3', 'exclsv', 'ttlfloor', 0.00],
                       ['stair',   '계단실',    'f3', 'exclsv', 'ttlfloor', 219.51],
                       ['berth',   'Berth',   'f3', 'exclsv', 'ttlfloor', 1_289.95],
                       ['mchnrm',  '기계실',    'f3', 'exclsv', 'ttlfloor', 0.00],
                       ['passage', '상하차통로', 'f3', 'common', 'nonfloor', 1_849.31],
                       ['ramp',    '램프',      'f3', 'common', 'ttlfloor', 0.00],
                       ['nmlstrg', '상온창고',   'f4', 'exclsv', 'ttlfloor', 4_621.30],
                       ['office',  '사무실',    'f4', 'exclsv', 'ttlfloor', 64.52],
                       ['canopy',  '캐노피',    'f4', 'exclsv', 'ttlfloor', 672.06],
                       ['stair',   '계단실',    'f4', 'exclsv', 'ttlfloor', 125.16],
                       ['berth',   'Berth',    'f4', 'exclsv', 'ttlfloor', 0.00],
                       ['mchnrm',  '기계실',    'f4', 'exclsv', 'ttlfloor', 0.00],
                       ['passage', '상하차통로', 'f4', 'common', 'ttlfloor', 0.00],
                       ['ramp',    '램프',      'f4', 'common', 'ttlfloor', 0.00],
                       ]
        
        self.rent_col = ['berth', 'canopy', 'cldstrg', 'nmlstrg', 'office', 'stair']
        self.rent_col_share = ['mchnrm']
        
    def _sorting_data(self):
        #### Analysis Data ####
        self.areadf = DataFrame(self.tmp_ary, columns=self.tmp_col)
        self.areatpl = self.areadf.area_m2.apply(lambda x: cf.Area(x))
        self.areadf['area_py'] = self.areatpl.apply(lambda x: x.py)
        self.areadf['area'] = self.areatpl.apply(lambda x: x.area)


    def _pivot_m2(self):
        tmp = self.areadf.pivot_table(index=['ttlfloor', 'floor'], columns=['exclsv', 'name'], values='area_m2')
        tmp[('ttl', 'sum')] = tmp.sum(axis=1)
        tmp[('exclsv', 'sum')] = tmp['exclsv'].sum(axis=1)
        tmp[('common', 'sum')] = tmp['common'].sum(axis=1)
        
        rent_col_tpl = [('exclsv', x) for x in self.rent_col]
        rent_sum_tpl = tmp[rent_col_tpl].sum(axis=1)
        rent_share_tpl = sum([tmp[('exclsv', x)].sum() for x in self.rent_col_share])
        rent_share_tpl = rent_sum_tpl / rent_sum_tpl.sum() * rent_share_tpl
        tmp[('rent', 'sum')] = rent_sum_tpl + rent_share_tpl
        
        mtrxsum = tmp.sum(axis=0)
        mtrxsum_ttlfloor = tmp.loc['ttlfloor'].sum(axis=0)
        mtrxsum_nonfloor = tmp.loc['nonfloor'].sum(axis=0)
        
        mtrxsum = DataFrame([mtrxsum, mtrxsum_ttlfloor, mtrxsum_nonfloor], 
                            index=[('ttl', 'sum'), ('ttlfloor', 'sum'), ('nonfloor', 'sum')],
                            columns=mtrxsum.index)
        tmp = tmp.append(mtrxsum)
        mtrxm2 = tmp.fillna(0)
        mtrxm2 = mtrxm2[[('exclsv', 'nmlstrg'),
                         ('exclsv', 'cldstrg'),
                         ('exclsv',  'canopy'),
                         ('exclsv',   'berth'),
                         ('exclsv',  'office'),
                         ('exclsv',   'stair'),
                         ('exclsv',  'mchnrm'),
                         ('exclsv',     'sum'),
                         ('common', 'passage'),
                         ('common',    'ramp'),
                         ('common',     'sum'),
                         (   'ttl',     'sum'),
                         (  'rent',     'sum')]]
        mtrxm2 = mtrxm2.reindex([('ttlfloor',  'b1'),
                                 ('ttlfloor',  'f1'),
                                 ('ttlfloor',  'f2'),
                                 ('ttlfloor',  'f3'),
                                 ('ttlfloor',  'f4'),
                                 ('ttlfloor', 'sum'),
                                 ('nonfloor',  'f1'),
                                 ('nonfloor',  'f3'),
                                 ('nonfloor', 'sum'),
                                 (     'ttl', 'sum'),
                                 ])
        self.aream2 = mtrxm2
        
    
    def _pivot_py(self):
        tmp = self.areadf.pivot_table(index=['ttlfloor', 'floor'], columns=['exclsv', 'name'], values='area_py')
        tmp[('ttl', 'sum')] = tmp.sum(axis=1)
        tmp[('exclsv', 'sum')] = tmp['exclsv'].sum(axis=1)
        tmp[('common', 'sum')] = tmp['common'].sum(axis=1)
        
        rent_col_tpl = [('exclsv', x) for x in self.rent_col]
        rent_sum_tpl = tmp[rent_col_tpl].sum(axis=1)
        rent_share_tpl = sum([tmp[('exclsv', x)].sum() for x in self.rent_col_share])
        rent_share_tpl = rent_sum_tpl / rent_sum_tpl.sum() * rent_share_tpl
        tmp[('rent', 'sum')] = rent_sum_tpl + rent_share_tpl
        
        mtrxsum = tmp.sum(axis=0)
        mtrxsum_ttlfloor = tmp.loc['ttlfloor'].sum(axis=0)
        mtrxsum_nonfloor = tmp.loc['nonfloor'].sum(axis=0)
        
        mtrxsum = DataFrame([mtrxsum, mtrxsum_ttlfloor, mtrxsum_nonfloor], 
                            index=[('ttl', 'sum'), ('ttlfloor', 'sum'), ('nonfloor', 'sum')],
                            columns=mtrxsum.index)
        tmp = tmp.append(mtrxsum)
        mtrxpy = tmp.fillna(0)
        mtrxpy = mtrxpy[[('exclsv', 'nmlstrg'),
                         ('exclsv', 'cldstrg'),
                         ('exclsv',  'canopy'),
                         ('exclsv',   'berth'),
                         ('exclsv',  'office'),
                         ('exclsv',   'stair'),
                         ('exclsv',  'mchnrm'),
                         ('exclsv',     'sum'),
                         ('common', 'passage'),
                         ('common',    'ramp'),
                         ('common',     'sum'),
                         (   'ttl',     'sum'),
                         (  'rent',     'sum')]]
        mtrxpy = mtrxpy.reindex([('ttlfloor',  'b1'),
                                 ('ttlfloor',  'f1'),
                                 ('ttlfloor',  'f2'),
                                 ('ttlfloor',  'f3'),
                                 ('ttlfloor',  'f4'),
                                 ('ttlfloor', 'sum'),
                                 ('nonfloor',  'f1'),
                                 ('nonfloor',  'f3'),
                                 ('nonfloor', 'sum'),
                                 (     'ttl', 'sum'),
                                 ])
        self.areapy = mtrxpy
        









