#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 07:27:24 2022

@author: KP_Hong
"""

import os
import sys
import xlsxwriter
from importlib import import_module

from datetime import date
import pandas as pd
from pandas import Series, DataFrame
import numpy as np

DIRECTORY = '/'.join(os.getcwd().split('/')[:-1])
sys.path.append(DIRECTORY)

pd.set_option('display.max_row', 200)
pd.set_option('display.max_columns', 30)

import cafle as cf
from cafle import Write, WriteWS, Cell
from cafle.genfunc import (
    rounding as R,
    PY,
    EmptyClass,
    )

dirname = "case1_220324/"
file_adrs = "exercse_todict.xlsx"
wb = Write(dirname + file_adrs)
ws = wb.add_ws("sample")

midx = pd.MultiIndex(levels=[["zero", "one"], ["x", "y"]], codes=[[1, 1, 0, 0], [1, 0, 1, 0]])
df = pd.DataFrame([[10, 20], [30, 20], [45, 65], [87, 90]], index=midx)

cell = Cell(0,0)
cell = wb.write(cell, "Title", wsname=ws)

#### from DataFrame to xlsxwrite ####
data = df.to_dict('split')
row = cell.row
col = cell.col

if isinstance(data['columns'][0], tuple):
    dfcolno = len(data['columns'][0])
else:
    dfcolno = 1
    
if isinstance(data['index'][0], tuple):
    dfidxno = len(data['index'][0])
else:
    dfidxno = 1

if dfcolno == 1:
    wb.write_row(Cell(row, col+dfidxno), data['columns'], fmt=None, wsname=ws)
elif dfcolno > 1:
    _row = row
    _col = col+dfidxno
    for valtpl in data['columns']:
        wb.write_col(Cell(_row, _col), valtpl, fmt=None, wsname=ws)
        _col += 1

if dfidxno == 1:
    wb.write_col(Cell(row+dfcolno, col), data['index'], fmt=None, wsname=ws)
elif dfidxno > 1:
    _row = row+dfcolno
    _col = col
    for valtpl in data['index']:
        wb.write_row(Cell(_row, _col), valtpl, fmt=None, wsname=ws)
        _row += 1

_row = row+dfcolno
_col = col+dfidxno
for valtpl in data['data']:
    wb.write_row(Cell(_row, _col), valtpl, fmt=None, wsname=ws)
    _row += 1

wb.close()






































