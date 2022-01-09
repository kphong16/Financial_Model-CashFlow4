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
PRTNAME = CASE+"_"+VERSION+"_"+DATE+".xlsx"
astn = EmptyClass()


#### Read Financing Data ####
fnc_mdl = import_module(CASE + ASTNFNC)
fnc = {}
fnc["idx"] = fnc_mdl.Idx()
idx = fnc["idx"].idx
fnc_mdl.idx = idx

fnc["equity"] = fnc_mdl.Equity(fnc["idx"])
equity = fnc["equity"].equity

fnc["loan"] = fnc_mdl.Loan(fnc["idx"])
loan = fnc["loan"].loan

fnc["loancst"] = fnc_mdl.FncCst_Loan(fnc["loan"])
loancst = fnc["loancst"]

fnc["fund"] = fnc_mdl.Fund(fnc["idx"])
fund = fnc["fund"].loan

fnc["fundcst"] = fnc_mdl.FncCst_Fund(fnc["fund"])
fundcst = fnc["fundcst"]

fnc["mrtg"] = fnc_mdl.Mrtg(fnc["idx"])
mrtg = fnc["mrtg"].loan

fnc["mrtgcst"] = fnc_mdl.FncCst_Mrtg(fnc["mrtg"])
mrtgcst = fnc["mrtgcst"]

#### Read Sales Data and Create Sales Accounts ####
sales_mdl = import_module(CASE + ASTNSLS)
sales_mdl.idx = idx
fnc["sales"] = sales_mdl.Sales()
sales = fnc["sales"]

#### Read Cost Data and Create Cost Accounts ####
cost_mdl = import_module(CASE + ASTNCST)
cost_mdl.idx = idx
fnc["cost"] = cost_mdl.Cost()
cost = fnc["cost"]

#### Read Operating Accounts Data and Create ####
acc_mdl = import_module(CASE + ASTNACC)
acc_mdl.idx = idx
fnc["acc"] = acc_mdl.Acc()
acc = fnc["acc"]


#### Execute Cash Flow ####
for idxno in idx:

    #################
    #### Sales ####
    for key, item in sales._dct.items():
        amt_scd = item.scd_out[idxno]
        item.send(idxno, amt_scd, acc.oprtg)

    #################
    #### PF Loan ####

    #### Loans: set loan withdrawble ####
    # If it's initial date then set loans withdrawble.
    equity.set_wtdrbl_intldate(idxno, idx[0])
    for rnk in fund.rnk:
        fund[rnk].set_wtdrbl_intldate(idxno)
    for rnk in loan.rnk:
        loan[rnk].set_wtdrbl_intldate(idxno)
    for rnk in mrtg.rnk:
        mrtg[rnk].set_wtdrbl_intldate(idxno)
    
    #### Expected Costs: calculate expected costs and add on scd_in ####
    # calculate operating costs on scd_in
    oprtg_cost = cost.mrg._df.scd_in[idxno]
    fncrsng_cost = loancst.mrg._df.scd_in[idxno]
    fndrsng_cost = fundcst.mrg._df.scd_in[idxno]
    mtgrsng_cost = mrtgcst.mrg._df.scd_in[idxno]
    
    # calculate financial costs on scd_in
    for rnk in loan.rnk:
        if idxno == loan[rnk].idxfn[0]:
            loan[rnk].fee.addscd(idxno, loan[rnk].fee.amt)
        if all([loan[rnk].is_wtdrbl, not loan[rnk].is_repaid]):
            loan[rnk].IR.addscd(idxno, loan[rnk].IRamt_topay(idxno))
            loan[rnk].fob.addscd(idxno, loan[rnk].fobamt_topay(idxno))
    
    for rnk in fund.rnk:
        if idxno == fund[rnk].idxfn[0]:
            fund[rnk].fee.addscd(idxno, fund[rnk].fee.amt)
        if all([fund[rnk].is_wtdrbl, not fund[rnk].is_repaid]):
            fund[rnk].IR.addscd(idxno, fund[rnk].IRamt_topay(idxno))
            fund[rnk].fob.addscd(idxno, fund[rnk].fobamt_topay(idxno))
    
    for rnk in mrtg.rnk:
        if idxno == mrtg[rnk].idxfn[0]:
            mrtg[rnk].fee.addscd(idxno, mrtg[rnk].fee.amt)
        if all([mrtg[rnk].is_wtdrbl, not mrtg[rnk].is_repaid]):
            mrtg[rnk].IR.addscd(idxno, mrtg[rnk].IRamt_topay(idxno))
            mrtg[rnk].fob.addscd(idxno, mrtg[rnk].fobamt_topay(idxno))
    
    # gather financial costs
    fncl_fee = loan.ttl.fee.scd_in[idxno]
    fncl_IR  = loan.ttl.IR.scd_in[idxno]
    fncl_fob = loan.ttl.fob.scd_in[idxno]
    
    fund_fee = fund.ttl.fee.scd_in[idxno]
    fund_IR  = fund.ttl.IR.scd_in[idxno]
    fund_fob = fund.ttl.fob.scd_in[idxno]
    
    mrtg_fee = mrtg.ttl.fee.scd_in[idxno]
    mrtg_IR  = mrtg.ttl.IR.scd_in[idxno]
    mrtg_fob = mrtg.ttl.fob.scd_in[idxno]

    # total costs
    cost_ttl = oprtg_cost + fncrsng_cost + fndrsng_cost \
               + fncl_fee + fncl_IR + fncl_fob \
               + fund_fee + fund_IR + fund_fob \
               + mrtg_fee + mrtg_IR + mrtg_fob
    
    
    #### Fund and Loans: withdraw cash from fund and loans ####
    # calculate the amount to withdraw
    amt_rqrd = acc.oprtg.amt_rqrd_excs(idxno, cost_ttl)
    
    # Withdraw loan amount
    amt_wtdrw = 0
    amt_wtdrw += equity.wtdrw(idxno, equity.amt_intl, acc.oprtg)
    
    for rnk in sorted(fund.rnk, reverse=True):
        amt_wtdrw += fund[rnk].wtdrw(idxno, fund[rnk].amt_intl, acc.oprtg)
    
    if idxno == idx.loan[0]:
        # withdraw initial loan amount
        for rnk in sorted(loan.rnk, reverse=True):
            amt_wtdrw += loan[rnk].wtdrw(idxno, loan[rnk].amt_intl, acc.oprtg)
    amt_rqrd = max(amt_rqrd - amt_wtdrw, 0)
    for rnk in sorted(loan.rnk, reverse=True):
        amt_rqrd = max(amt_rqrd - loan[rnk].wtdrw(idxno, amt_rqrd, acc.oprtg), 0)
    
    if idxno == idx.mrtg[0]:
        # withdraw initial mrtg amount
        for rnk in sorted(mrtg.rnk, reverse=True):
            amt_wtdrw += mrtg[rnk].wtdrw(idxno, mrtg[rnk].amt_intl, acc.repay)
    amt_rqrd = max(amt_rqrd - amt_wtdrw, 0)
    for rnk in sorted(mrtg.rnk, reverse=True):
        amt_rqrd = max(amt_rqrd - mrtg[rnk].wtdrw(idxno, amt_rqrd, acc.repay), 0)
    
    #### Costs: 토지비, 공사비 등 각종 비용 지출 ####
    for key, item in cost._dct.items():
        for k, _acc in item.dct.items():
            amt_scd = _acc.scd_in[idxno]
            acc.oprtg.send(idxno, amt_scd, _acc)
    
    #### Finance Raising Cost: 금융조달비용 지출 ####
    for key, item in loancst._dct.items():
        amt_scd = item.scd_in[idxno]
        acc.oprtg.send(idxno, amt_scd, item)
    
    for key, item in fundcst._dct.items():
        amt_scd = item.scd_in[idxno]
        acc.oprtg.send(idxno, amt_scd, item)
    
    for key, item in mrtgcst._dct.items():
        amt_scd = item.scd_in[idxno]
        acc.oprtg.send(idxno, amt_scd, item)
    
        
    #### Loans: pay financial cost ####
    for rnk in loan.rnk:
        acc.oprtg.send(idxno, loan[rnk].fee.scd_in[idxno], loan[rnk].fee)
        acc.oprtg.send(idxno, loan[rnk].IR.scd_in[idxno], loan[rnk].IR)
        acc.oprtg.send(idxno, loan[rnk].fob.scd_in[idxno], loan[rnk].fob)
    
    for rnk in fund.rnk:
        acc.oprtg.send(idxno, fund[rnk].fee.scd_in[idxno], fund[rnk].fee)
        acc.oprtg.send(idxno, fund[rnk].IR.scd_in[idxno], fund[rnk].IR)
        acc.oprtg.send(idxno, fund[rnk].fob.scd_in[idxno], fund[rnk].fob)
        
    for rnk in mrtg.rnk:
        acc.oprtg.send(idxno, mrtg[rnk].fee.scd_in[idxno], mrtg[rnk].fee)
        acc.oprtg.send(idxno, mrtg[rnk].IR.scd_in[idxno], mrtg[rnk].IR)
        acc.oprtg.send(idxno, mrtg[rnk].fob.scd_in[idxno], mrtg[rnk].fob) 
        
    #### Loans: repay loan amount ####
    if loan.is_repaid is False:
        if acc.repay.bal_end[idxno] >= 0: # 상환계좌에 현금이 있는 경우
            for rnk in loan.rnk:
                if rnk == 0 or loan[rnk-1].is_repaid:
                    amtrpy = loan[rnk].amt_repay(idxno, acc.repay.bal_end[idxno])
                    acc.repay.send(idxno, amtrpy, loan[rnk].ntnl)
                    loan[rnk].set_repaid(idxno)
                if loan.is_repaid is True:
                    acc.repay.send(idxno, acc.repay.bal_end[idxno], acc.oprtg)
                
        if idxno >= loan.idxfn[-1]: # 만기 도래한 경우
            for rnk in loan.rnk:
                if rnk == 0 or loan[rnk-1].is_repaid:
                    amtrpy = loan[rnk].amt_rpy_exptd(idxno)
                    acc.oprtg.send(idxno, amtrpy, loan[rnk].ntnl)
                    loan[rnk].set_repaid(idxno)
    
    #### Loans: Set back loan unwithdrawble at maturity ####
    # If it was maturity date then set back loan unwithdrawble.
    equity.setback_wtdrbl_mtrt(idxno)
    for rnk in loan.rnk:
        loan[rnk].setback_wtdrbl_mtrt(idxno)
    for rnk in fund.rnk:
        fund[rnk].setback_wtdrbl_mtrt(idxno)
    for rnk in mrtg.rnk:
        mrtg[rnk].setback_wtdrbl_mtrt(idxno)
        
    #### Equity: repay investment amount ####
    if idxno == idx[-1]: # 사업 마지막 구간
        _is_repaid = True
        if loan.is_repaid is True:
            acc.oprtg.send(idxno, acc.oprtg.bal_end[idxno], equity.ntnl)


#### Print out the results ####
rslt_mdl    = import_module(CASE + RESULT)

rslt        = rslt_mdl.WriteCF(PRTNAME, fnc)

        
        
        
        
        