#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 13:15:43 2021

@author: KP_Hong
"""
import os
import sys
import pickle
import xlsxwriter
from datetime import datetime
from importlib import import_module
import pandas as pd
from pandas import Series, DataFrame
import numpy as np

directory = '/'.join(os.getcwd().split('/')[:-1])
sys.path.append(directory)

pd.set_option('display.max_row', 200)
pd.set_option('display.max_columns', 100)

import cafle as cf
from cafle.genfunc import rounding as R
from cafle.genfunc import PY
from cafle.genfunc import EmptyClass


#### Initial Setting ####
dirname = os.getcwd().split('/')[-1]
CASE = dirname # directory name
VERSION = "v1.0"

ASTNFNC = ".astn_financing"
ASTNSLS = ".astn_sales"
ASTNCST = ".astn_cost"
ASTNACC = ".astn_account"
RESULT  = ".astn_output"
DATE = datetime.now().strftime('%y%m%d')
#DATE = "211221"
PRTNAME = "rslt_"+VERSION+"_"+DATE+".xlsx"
astn = EmptyClass()


#### Read Assumption Data ####
fnc = import_module(CASE + ASTNFNC).Intlz()
rnt = import_module(CASE + ASTNSLS).Intlz(fnc.idx)




