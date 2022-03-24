#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

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
from cafle import Account
from cafle.genfunc import (
    rounding as R,
    PY,
    EmptyClass,
    )
    
    
#### Initial Setting ####

dirname = os.getcwd().split('/')[-1]
CASE = dirname # directory name
VERSION = "v1.0"

ASTNFNC = ".astn_financing"
ASTNSLS = ".astn_sales"
ASTNCST = ".astn_cost"
ASTNACC = ".astn_account"
OUTPUT  = ".astn_output"
ASTNAREA    = ".astn_area"
DATE = date.today().strftime('%y%m%d')
PRTNAME = "output_" + VERSION + "_" + DATE + ".xlsx"
astn = EmptyClass()


#### Read Area Data ####
mdl_area = import_module(CASE + ASTNAREA)
astn.area = mdl_area.area
area = astn.area

#### Read Financing Data ####
mdl_fnc = import_module(CASE + ASTNFNC)

astn.idx = mdl_fnc.idx
idx = astn.idx

astn.equity = mdl_fnc.Equity().equity
equity = astn.equity

astn.loan = mdl_fnc.Loan().loan
loan = astn.loan

astn.loancst = mdl_fnc.LoanCst(astn.loan)
loancst = astn.loancst


#### Read Sales Data and Create Sales Accounts ####
mdl_sales = import_module(CASE + ASTNSLS)
astn.sales = mdl_sales.Sales()
sales = astn.sales


#### Read Cost Data and Create Cost Accounts ####
mdl_cost = import_module(CASE + ASTNCST)
astn.cost = mdl_cost.Cost()
cost = astn.cost

#### Read Operating Accounts Data and Create ####
mdl_acc = import_module(CASE + ASTNACC)
astn.acc = mdl_acc.Acc()
acc = astn.acc


#### Execution of Cash Flow ####
for idxno in idx.prjt:
    
    #### Sales ####
    for key, item in sales.dct.items():
        amt_scd = item.scd_out[idxno]
        item.send(idxno, amt_scd, acc.repay)
        
        
    #### PF Loan ####
    ## Set loan withdrawable
    # If it's initial date then set loans withdrawable.
    equity.set_wtdrbl_intldate(idxno, idx.prjt[0])
    for rnk in loan.rnk():
        loan.by_rnk(rnk).set_wtdrbl_intldate(idxno)
        
    ## Expected costs amount : calculate expected costs and add on scd_in
    # calculate operating costs on scd_in
    _cost_oprtg = cost.mrg.scd_in[idxno]
    _cost_loancst = loancst.mrg.scd_in[idxno]
    
    # calculate financial costs and set on scd_in.
    for rnk in loan.rnk():
        _loan = loan.by_rnk(rnk)
        if idxno == idx.loan[0]:
            _loan.fee.addscd(idxno, _loan.fee.amt)
        if all([_loan.is_wtdrbl, not _loan.is_repaid]):
            _loan.IR.addscd(idxno, _loan.IRamt_topay(idxno))
            _loan.fob.addscd(idxno, _loan.fobamt_topay(idxno))
    _cost_loanfee   = loan.mrgloans().fee.scd_in[idxno]
    _cost_loanIR    = loan.mrgloans().IR.scd_in[idxno]
    _cost_loanfob   = loan.mrgloans().fob.scd_in[idxno]
            
    # total expected costs
    _cost_ttl = _cost_oprtg + _cost_loancst \
                + _cost_loanfee + _cost_loanIR + _cost_loanfob
    _amt_rqrd = acc.oprtg.amt_rqrd_excs(idxno, _cost_ttl)
    
    ## Withdraw loans
    # withdraw equity amount
    _amt_wtdrw = 0
    _amt_wtdrw += equity.wtdrw(idxno, equity.amt_intl, acc.oprtg)
    
    # withdraw loan amount
    if idxno == idx.loan[0]:
        for rnk in loan.rnk(reverse=True):
            _loan = loan.by_rnk(rnk)
            _amt_wtdrw += _loan.wtdrw(idxno, _loan.amt_intl, acc.oprtg)
    _amt_rqrd = max(_amt_rqrd - _amt_wtdrw, 0)
    
    for rnk in loan.rnk(reverse=True):
        _loan = loan.by_rnk(rnk)
        _amt_wtdrw = _loan.wtdrw(idxno, _amt_rqrd, acc.oprtg)
        _amt_rqrd = max(_amt_rqrd - _amt_wtdrw, 0)
        
    ## Pay operating costs
    for key, item in cost.dct.items():
        _amt_scd = item.scd_in[idxno]
        acc.oprtg.send(idxno, _amt_scd, item)
            
    ## Pay financial costs
    for key, item in loancst.dct.items():
        _amt_scd = item.scd_in[idxno]
        acc.oprtg.send(idxno, _amt_scd, item)
    
    for rnk in loan.rnk():
        _loan = loan.by_rnk(rnk)
        acc.oprtg.send(idxno, _loan.fee.scd_in[idxno], _loan.fee)
        acc.oprtg.send(idxno, _loan.IR.scd_in[idxno], _loan.IR)
        acc.oprtg.send(idxno, _loan.fob.scd_in[idxno], _loan.fob)
    
    ## Repay loan amount
    if loan.is_repaid_all() is False:
        if acc.repay.bal_end[idxno] >= 0:
            for rnk in loan.rnk():
                _loan = loan.by_rnk(rnk)
                if rnk == 0 or loan.by_rnk(rnk-1).is_repaid:
                    _amtrpy = _loan.amt_repay(idxno, acc.repay.bal_end[idxno])
                    acc.repay.send(idxno, _amtrpy, _loan.ntnl)
                    _loan.set_repaid(idxno)
                if loan.is_repaid is True:
                    acc.repay.send(idxno, acc.repay.bal_end[idxno], acc.oprtg)
        if idxno >= idx.loan[-1]: # at maturity
            for rnk in loan.rnk():
                _loan = loan.by_rnk(rnk)
                _amtrpy = _loan.amt_rpy_exptd(idxno)
                acc.oprtg.send(idxno, _amtrpy, _loan.ntnl)
                _loan.set_repaid(idxno)
    if loan.is_repaid_all() is True:
        _amtrpy = acc.repay.bal_end[idxno]
        acc.repay.send(idxno, _amtrpy, acc.oprtg)
    
    ## Set back loans unwithdrawable at maturity
    equity.setback_wtdrbl_mtrt(idxno)
    for rnk in loan.rnk():
        loan.by_rnk(rnk).setback_wtdrbl_mtrt(idxno)
        
    ## Pay return on the investment
    if idxno == idx.prjt[-1]:
        _is_repaid = True
        if loan.is_repaid is True:
            acc.oprtg.send(idxno, acc.oprtg.bal_end[idxno], equity.ntnl)
print("Cashflow calculation finished.")            

#### Print Out the Results ####
mdl_output  = import_module(CASE + OUTPUT)
output      = mdl_output.WriteCF(PRTNAME, astn)
        



































