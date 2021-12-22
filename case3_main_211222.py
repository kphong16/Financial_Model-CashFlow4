#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 13:15:43 2021

@author: KP_Hong
"""

import json
import pickle
import xlsxwriter
from datetime import datetime
from importlib import import_module
import pandas as pd
from pandas import Series, DataFrame
import numpy as np

pd.set_option('display.max_row', 200)
pd.set_option('display.max_columns', 100)

import cafle as cf
from cafle.genfunc import rounding as R
from cafle.genfunc import PY
from cafle.genfunc import EmptyClass
from cafle.genfunc import read_json


#### Initial Setting ####
CASE = "case3" # directory name
VERSION = "v3.0_PlanB"

ASTNFNC = ".astn_financing_211222_PlanB"
ASTNCST = ".astn_cost_211222_PlanB"
ASTNSLS = ".astn_sales_211222_PlanB"
ASTNACC = ".astn_account_211222_PlanB"
ASTNOVW = ".astn_overview_211222_PlanB"
DATE = datetime.now().strftime('%y%m%d')
#DATE = "211221"
PRTNAME = "/"+CASE+"_"+VERSION+"_"+DATE+".xlsx"
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

fnc["fnccst"] = fnc_mdl.FncCst(fnc["loan"])
fnccst = fnc["fnccst"]


#### Read Sales Data ####
sales_mdl = import_module(CASE + ASTNSLS)
sales_mdl.idx = idx
sales = sales_mdl.Sales().sales["account"]


#### Read Cost Data and Create Cost Accounts ####
cost_mdl = import_module(CASE + ASTNCST)
cost_mdl.idx = idx
cost = cost_mdl.Cost()


#### Read Operating Accounts Data and Create ####
acc_mdl = import_module(CASE + ASTNACC)
acc_mdl.idx = idx
acc = acc_mdl.Acc()


#### Read Overview Data ####
ovw_mdl = import_module(CASE + ASTNOVW)
ovw = ovw_mdl.Area()
bsns = ovw.bsns
area = ovw.areadf
aream2 = ovw.aream2
areapy = ovw.areapy


#### Execute Cash Flow ####
for idxno in idx.index:
    #### Loans: set loan withdrawble ####
    # If it's initial date then set loans withdrawble.
    equity.set_wtdrbl_intldate(idxno, idx[0])
    for rnk in loan.rnk:
        loan[rnk].set_wtdrbl_intldate(idxno)
        
        
    #####################
    #### Bridge Loan ####
    #### Cash Inflow: cash inflow from PF_Loan ####
    #salesamt = sales.sub_scdd[idxno]
    #if salesamt > 0:
    #    sales.send(idxno, salesamt, acc.repay)
        
    #### Expected Costs: calculate expected costs ####
    # calculate operating costs on add_scdd
    _oprtg_cost = [_acc.add_scdd[idxno] for _acc in cost.lfkey("account")]
    oprtg_cost = sum(_oprtg_cost)
    
    _fncrsng_cost = [_acc.add_scdd[idxno] for _acc in fnccst.lfkey("account")]
    fncrsng_cost = sum(_fncrsng_cost)
    
    # calculate financial costs on add_scdd
    for rnk in loan.rnk:
        if idxno == loan[rnk].idxfn[0]:
            loan[rnk].fee.addscdd(idxno, loan[rnk].fee.amt)
        if all([loan[rnk].is_wtdrbl, not loan[rnk].is_repaid]):
            loan[rnk].IR.addscdd(idxno, loan[rnk].IRamt_topay(idxno))
            loan[rnk].fob.addscdd(idxno, loan[rnk].fobamt_topay(idxno))
    
    # gather financial costs
    fncl_fee = loan.ttl.fee.add_scdd[idxno]
    fncl_IR = loan.ttl.IR.add_scdd[idxno]
    fncl_fob = loan.ttl.fob.add_scdd[idxno]

    cost_ttl = oprtg_cost + fncrsng_cost + fncl_fee + fncl_IR + fncl_fob
        
    
    #### Loans: withdraw loan ####
    # calculate the amount to withdraw
    amt_rqrd = acc.oprtg.amt_rqrd_excess(idxno, cost_ttl)
    
    # Withdraw loan amount
    amt_wtdrw = 0
    amt_wtdrw += equity.wtdrw(idxno, equity.amt_intl, acc.oprtg)
    if idxno == idx.loan[0]:
        # withdraw initial loan amount
        for rnk in sorted(loan.rnk, reverse=True):
            amt_wtdrw += loan[rnk].wtdrw(idxno, loan[rnk].amt_intl, acc.oprtg)
    
    amt_rqrd = max(amt_rqrd - amt_wtdrw, 0)
    for rnk in sorted(loan.rnk, reverse=True):
        amt_rqrd = max(amt_rqrd - loan[rnk].wtdrw(idxno, amt_rqrd, acc.oprtg), 0)
        
    
    #### Costs: 토지비, 공사비 등 각종 비용 지출 ####
    lst_cst = cost.lfkey("account")
    for cst in lst_cst:
        amt_scdd = cst.add_scdd[idxno]
        acc.oprtg.send(idxno, amt_scdd, cst)
    
    #### Finance Raising Cost: 금융조달비용 ####
    lst_fncrsng = fnccst.lfkey("account")
    for fncrsng in lst_fncrsng:
        amt_scdd = fncrsng.add_scdd[idxno]
        acc.oprtg.send(idxno, amt_scdd, fncrsng)
        
    #### Loans: pay financial cost ####
    for rnk in loan.rnk:
        acc.oprtg.send(idxno, loan[rnk].fee.add_scdd[idxno], loan[rnk].fee)
        
    for rnk in loan.rnk:
        acc.oprtg.send(idxno, loan[rnk].IR.add_scdd[idxno], loan[rnk].IR)
        
    for rnk in loan.rnk:
        acc.oprtg.send(idxno, loan[rnk].fob.add_scdd[idxno], loan[rnk].fob)
        
        
    #### Loans: repay loan amount ####
    if idxno >= loan.idxfn[-1]: # 만기 도래 여부 확인
        for rnk in loan.rnk:
            if rnk == 0 or loan[rnk-1].is_repaid:
                amtrpy = loan[rnk].repay_amt(idxno, acc.repay.bal_end[idxno])
                acc.repay.send(idxno, amtrpy, loan[rnk].ntnl)
                loan[rnk].set_repaid(idxno)
        
            if rnk == max(loan.rnk):
                acc.repay.send(idxno, acc.repay.bal_end[idxno], acc.oprtg)
        
    
    #### Loans: Set back loan unwithdrawble at maturity ####
    # If it was maturity date then set back loan unwithdrawble.
    equity.setback_wtdrbl_mtrt(idxno)
    for rnk in loan.rnk:
        loan[rnk].setback_wtdrbl_mtrt(idxno)
    
    
    
    #################
    #### PF Loan ####
    
    #### Cash Inflow: cash inflow from sales or rent etc. ####
    salesamt = sales.sub_scdd[idxno]
    if salesamt > 0:
        sales.send(idxno, salesamt, acc.repay)
        
    #### Expected Costs: calculate expected costs ####
    # calculate operating costs on add_scdd
    _oprtg_cost = [_acc.add_scdd[idxno] for _acc in cost.lfkey("account")]
    oprtg_cost = sum(_oprtg_cost)
    
    _fncrsng_cost = [_acc.add_scdd[idxno] for _acc in fnccst.lfkey("account")]
    fncrsng_cost = sum(_fncrsng_cost)
    
    # calculate financial costs on add_scdd
    for rnk in loan.rnk:
        if idxno == loan[rnk].idxfn[0]:
            loan[rnk].fee.addscdd(idxno, loan[rnk].fee.amt)
        if all([loan[rnk].is_wtdrbl, not loan[rnk].is_repaid]):
            loan[rnk].IR.addscdd(idxno, loan[rnk].IRamt_topay(idxno))
            loan[rnk].fob.addscdd(idxno, loan[rnk].fobamt_topay(idxno))
    
    # gather financial costs
    fncl_fee = loan.ttl.fee.add_scdd[idxno]
    fncl_IR = loan.ttl.IR.add_scdd[idxno]
    fncl_fob = loan.ttl.fob.add_scdd[idxno]

    cost_ttl = oprtg_cost + fncrsng_cost + fncl_fee + fncl_IR + fncl_fob
        
    
    #### Loans: withdraw loan ####
    # calculate the amount to withdraw
    amt_rqrd = acc.oprtg.amt_rqrd_excess(idxno, cost_ttl)
    
    # Withdraw loan amount
    amt_wtdrw = 0
    amt_wtdrw += equity.wtdrw(idxno, equity.amt_intl, acc.oprtg)
    if idxno == idx.loan[0]:
        # withdraw initial loan amount
        for rnk in sorted(loan.rnk, reverse=True):
            amt_wtdrw += loan[rnk].wtdrw(idxno, loan[rnk].amt_intl, acc.oprtg)
    
    amt_rqrd = max(amt_rqrd - amt_wtdrw, 0)
    for rnk in sorted(loan.rnk, reverse=True):
        amt_rqrd = max(amt_rqrd - loan[rnk].wtdrw(idxno, amt_rqrd, acc.oprtg), 0)
        
    
    #### Costs: 토지비, 공사비 등 각종 비용 지출 ####
    lst_cst = cost.lfkey("account")
    for cst in lst_cst:
        amt_scdd = cst.add_scdd[idxno]
        acc.oprtg.send(idxno, amt_scdd, cst)
    
    #### Finance Raising Cost: 금융조달비용 ####
    lst_fncrsng = fnccst.lfkey("account")
    for fncrsng in lst_fncrsng:
        amt_scdd = fncrsng.add_scdd[idxno]
        acc.oprtg.send(idxno, amt_scdd, fncrsng)
        
    #### Loans: pay financial cost ####
    for rnk in loan.rnk:
        acc.oprtg.send(idxno, loan[rnk].fee.add_scdd[idxno], loan[rnk].fee)
        
    for rnk in loan.rnk:
        acc.oprtg.send(idxno, loan[rnk].IR.add_scdd[idxno], loan[rnk].IR)
        
    for rnk in loan.rnk:
        acc.oprtg.send(idxno, loan[rnk].fob.add_scdd[idxno], loan[rnk].fob)
        
        
    #### Loans: repay loan amount ####
    if idxno >= loan.idxfn[-1]: # 만기 도래 여부 확인
        for rnk in loan.rnk:
            if rnk == 0 or loan[rnk-1].is_repaid:
                amtrpy = loan[rnk].repay_amt(idxno, acc.repay.bal_end[idxno])
                acc.repay.send(idxno, amtrpy, loan[rnk].ntnl)
                loan[rnk].set_repaid(idxno)
        
            if rnk == max(loan.rnk):
                acc.repay.send(idxno, acc.repay.bal_end[idxno], acc.oprtg)
        
    
    #### Loans: Set back loan unwithdrawble at maturity ####
    # If it was maturity date then set back loan unwithdrawble.
    equity.setback_wtdrbl_mtrt(idxno)
    for rnk in loan.rnk:
        loan[rnk].setback_wtdrbl_mtrt(idxno)
        
    #### Equity: repay investment amount ####
    if idxno == idx[-1]: # 사업 마지막 구간
        _is_repaid = True
        for rnk in loan.rnk:
            if not loan[rnk].is_repaid:
                _is_repaid = False
        if _is_repaid:
            acc.oprtg.send(idxno, acc.oprtg.bal_end[idxno], equity.ntnl)


#### Print out the results ####
rslt_mdl = import_module(CASE + ".output_result")
rslt_mdl.idx = idx
rslt_mdl.equity = equity
rslt_mdl.loan = loan
rslt_mdl.sales = sales
rslt_mdl.fnccst = fnccst
rslt_mdl.cost = cost
rslt_mdl.acc = acc
rslt_mdl.ovw = ovw
rslt = rslt_mdl.WriteCF(CASE + PRTNAME)


        
        
        
        
        