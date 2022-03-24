#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import os
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
    Area,
    EmptyClass,
    )
    

class AreaMtrx(Assumption_Base):
    def __init__(self):
        super().__init__()
        
        DIRECTORY = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        filename = "/data/area.csv"
        fileloc = DIRECTORY + filename
        
        self.rawdata = pd.read_csv(fileloc)
        self.rawdata['area_py'] = self.rawdata.area.apply(lambda x: Area(m2=x).py)
        
        self.mtrxd = self._set_mtrx(valname='area')
        self.mtrx  = self._prt_mtrx(self.mtrxd)
        self.rent  = self.mtrxd['rent'].groupby(level=1).sum()
        
        self.mtrxpyd = self._set_mtrx(valname='area_py')
        self.mtrxpy  = self._prt_mtrx(self.mtrxpyd)
        self.rentpy  = self.mtrxpyd['rent'].groupby(level=1).sum()
        
        
    def _set_mtrx(self, valname='area'):
        _mtrx = self.rawdata.pivot_table(
            index   = ['ttlfloor', 'floor'], 
            columns = ['exclsv', 'name'], 
            values  = valname,
            aggfunc = 'sum')
        _mtrx[('ttl', 'sum')] = _mtrx.sum(axis=1)
        _mtrx[('exclsv', 'sum')] = _mtrx['exclsv'].sum(axis=1)
        _mtrx[('common', 'sum')] = _mtrx['common'].sum(axis=1)
        
        # Calculation rent area
        rent_col = ['berth', 'canopy', 'cldstrg', 'nmlstrg', 'office', 'stair']
        rent_col_share = ['mchnrm']
        
        rent_col_tpl = [('exclsv', x) for x in rent_col]
        rent_sum_tpl = _mtrx[rent_col_tpl].sum(axis=1)
        rent_share_tpl = sum([_mtrx[('exclsv', x)].sum() for x in rent_col_share])
        rent_share_tpl = rent_sum_tpl / rent_sum_tpl.sum() * rent_share_tpl
        _mtrx[('rent', 'sum')] = rent_sum_tpl + rent_share_tpl
        _mtrx = _mtrx.fillna(0)
        
        _mtrx = _mtrx[[('exclsv', 'nmlstrg'),
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
        _mtrx = _mtrx.reindex([
                         ('ttlfloor',  'b1'),
                         ('ttlfloor',  'f1'),
                         ('ttlfloor',  'f2'),
                         ('ttlfloor',  'f3'),
                         ('ttlfloor',  'f4'),
                         ('nonfloor',  'f1'),
                         ('nonfloor',  'f3'),
                         ])
        
        return _mtrx
        
        
    def _prt_mtrx(self, _mtrx):
        _mtrxsum = _mtrx.sum(axis=0)
        _mtrxsum_ttlfloor = _mtrx.loc['ttlfloor'].sum(axis=0)
        _mtrxsum_nonfloor = _mtrx.loc['nonfloor'].sum(axis=0)

        _mtrxsum = DataFrame([_mtrxsum, _mtrxsum_ttlfloor, _mtrxsum_nonfloor], 
                        index=[('ttl', 'sum'), ('ttlfloor', 'sum'), ('nonfloor', 'sum')],
                        columns=_mtrxsum.index)
        _mtrx = _mtrx.append(_mtrxsum)
        _mtrx = _mtrx.fillna(0)
        
        _mtrx = _mtrx[[('exclsv', 'nmlstrg'),
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
        _mtrx = _mtrx.reindex([
                         ('ttlfloor',  'b1'),
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
        
        return _mtrx
        
area = AreaMtrx()
        
        
        
        
        
        
        