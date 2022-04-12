"""
Created on 2022-03-30
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
from cafle import (
    Account,
)
from cafle.genfunc import (
    rounding as R,
    PY,
    EmptyClass,
)

#### Initial Setting ####
DIRNAME     = os.getcwd().split('/')[-1]
VERSION     = "v1_dtld_220412"
ASTNFILE    = ".astn_" + VERSION
OUTPUTFILE  = ".output_v1_220330"
DATE        = date.today().strftime('%y%m%d')
PRTNAME     = "result_" + VERSION + "_" + DATE + ".xlsx"

astn = EmptyClass()

#### Load Assumption Data ####
mdl_astn      = import_module(DIRNAME + ASTNFILE)

land = mdl_astn.land
astn.land   = land

area = mdl_astn.area
astn.area   = area

idx = mdl_astn.idx
astn.idx    = idx

equity = mdl_astn.equity
astn.equity = equity

loan = mdl_astn.loan
astn.loan   = loan

loancst = mdl_astn.loancst
astn.loancst = loancst

sales = mdl_astn.sales
astn.sales = sales

cost = mdl_astn.cost
astn.cost = cost

acc = mdl_astn.acc
astn.acc = acc

def recognize_sales():
    for sales_each in sales.dct.values():
        amt_scd = sales_each.scd_out[idxno]
        sales_each.send(idxno, amt_scd, acc.repay)

def set_loan_withdrawable():
    equity.set_wtdrbl_intldate(idxno, idx.prjt[0])
    for rnk in loan.rnk:
        loan.by_rnk(rnk).set_wtdrbl_intldate(idxno)

def setback_loan_unwithdrawable():
    equity.setback_wtdrbl_mtrt(idxno)
    for rnk in loan.rnk:
        loan.by_rnk(rnk).setback_wtdrbl_mtrt(idxno)

def estimate_oprtgcst():
    return cost.mrg.scd_in[idxno]

def estimate_loancst():
    return loancst.mrg.scd_in[idxno]

def estimate_loan_expense():
    for rnk in loan.rnk:
        _loan = loan.by_rnk(rnk)
        if idxno == idx.loan[0]:
            _loan.fee.addscd(idxno, _loan.fee.amt)
        elif all([_loan.is_wtdrbl, not _loan.is_repaid]):
            _loan.IR.addscd(idxno, _loan.IRamt_topay(idxno))
            _loan.fob.addscd(idxno, _loan.fobamt_topay(idxno))
    _loanfee = loan.mrgloans().fee.scd_in[idxno]
    _loanIR  = loan.mrgloans().IR.scd_in[idxno]
    _loanfob = loan.mrgloans().fob.scd_in[idxno]
    return _loanfee + _loanIR + _loanfob

def withdraw_equity_amount():
    global amt_wtdrw
    amt_wtdrw += equity.wtdrw(idxno, equity.amt_intl, acc.oprtg)

def withdraw_loan_amount():
    global amt_wtdrw, amt_rqrd
    if idxno == idx.loan[0]:
        for rnk in sorted(loan.rnk, reverse=True):
            _loan = loan.by_rnk(rnk)
            amt_wtdrw += _loan.wtdrw(idxno, _loan.amt_intl, acc.oprtg)
    amt_rqrd = max(amt_rqrd - amt_wtdrw, 0)

    for rnk in sorted(loan.rnk, reverse=True):
        _loan = loan.by_rnk(rnk)
        amt_wtdrw = _loan.wtdrw(idxno, amt_rqrd, acc.oprtg)
        amt_rqrd = max(amt_rqrd - amt_wtdrw, 0)

def pay_loancst():
    for cst_each in loancst.dct.values():
        amt_scd = cst_each.scd_in[idxno]
        acc.oprtg.send(idxno, amt_scd, cst_each)

def pay_loan_expense():
    for rnk in loan.rnk:
        _loan = loan.by_rnk(rnk)
        acc.oprtg.send(idxno, _loan.fee.scd_in[idxno], _loan.fee)
        acc.oprtg.send(idxno, _loan.IR.scd_in[idxno], _loan.IR)
        acc.oprtg.send(idxno, _loan.fob.scd_in[idxno], _loan.fob)

def pay_oprtgcst():
    for cst_each in cost.dct.values():
        amt_scd = cst_each.scd_in[idxno]
        acc.oprtg.send(idxno, amt_scd, cst_each)

def repay_loan_amount():
    if acc.repay.bal_end[idxno] > 0:
        for rnk in loan.rnk:
            _loan = loan.by_rnk(rnk)
            if rnk == 0 or loan.by_rnk(rnk-1).is_repaid:
                amtrpy = _loan.amt_repay(idxno, acc.repay.bal_end[idxno])
                acc.repay.send(idxno, amtrpy, _loan.ntnl)
                _loan.set_repaid(idxno)
            #if loan.is_repaid is True:
            #    acc.repay.send(idxno, acc.repay.bal_end[idxno], acc.oprtg)
    if idxno >= idx.loan[-1]: # at maturity
        for rnk in loan.rnk:
            _loan = loan.by_rnk(rnk)
            amtrpy = _loan.amt_rpy_exptd(idxno)
            acc.oprtg.send(idxno, amtrpy, _loan.ntnl)
            _loan.set_repaid(idxno)

def send_repay_to_oprtg():
    amtrpy = acc.repay.bal_end[idxno]
    acc.repay.send(idxno, amtrpy, acc.oprtg)

def pay_profit_on_equity():
    if idxno == idx.prjt[-1]:
        if loan.is_repaid_all() is True:
            acc.oprtg.send(idxno, acc.oprtg.bal_end[idxno], equity.ntnl)

#### Execution of Cash Flow ####
for idxno in idx.prjt:
    ## Sales
    recognize_sales()

    ## Set loan withdrawable
    set_loan_withdrawable()

    ## Calculate estimated costs
    oprtg_cost = estimate_oprtgcst()
    loan_cost = estimate_loancst()
    loan_expense = estimate_loan_expense()
    estimated_cost_ttl = oprtg_cost + loan_cost + loan_expense
    amt_rqrd = acc.oprtg.amt_rqrd_excs(idxno, estimated_cost_ttl)

    ## Withdraw equity and loans
    amt_wtdrw = 0
    withdraw_equity_amount()
    withdraw_loan_amount()

    ## Pay loan and operating costs
    pay_loancst()
    pay_loan_expense()
    pay_oprtgcst()

    ## Repay loan
    if loan.is_repaid_all() is False:
        repay_loan_amount()
    if loan.is_repaid_all() is True:
        send_repay_to_oprtg()

    ## Setback loan unwithdrawable
    setback_loan_unwithdrawable()

    ## Pay profit on the equity investors
    pay_profit_on_equity()

    print(f"Working index: {idxno}", end='\r')
print("\nCashflow calculation is finished.")

#### Generate output file
mdl_output    = import_module(DIRNAME + OUTPUTFILE)
output = mdl_output.WriteCF(PRTNAME, astn)
print(f"Output file '{PRTNAME}' is generated.")

















