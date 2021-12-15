#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 13:15:43 2021

@author: KP_Hong
"""

import json
import pickle
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
CASE = "case1"
astn = EmptyClass()


#### Read Financing Data ####
import case1.astn_financing as fnc_mdl
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
import case1.astn_sales as sales_mdl
sales_mdl.idx = idx
sales = sales_mdl.Sales().sales["account"]


#### Read Cost Data and Create Cost Accounts ####
import case1.astn_cost as cost_mdl
cost_mdl.idx = idx
cost = cost_mdl.Cost()


#### Read Operating Accounts Data and Create ####
import case1.astn_account as acc_mdl
acc_mdl.idx = idx
acc = acc_mdl.Acc()


#### Execute Cash Flow ####
for idxno in idx.index:
    #### Loans: set loan withdrawble ####
    # If it's initial date then set loan withdrawble.
    equity.set_wtdrbl_intldate(idxno, idx[0])
    for rnk in loan.rnk:
        loan[rnk].set_wtdrbl_intldate(idxno)
        
    #### Cash Inflow: cash inflow from sales or rent etc. ####
    salesamt = sales.sub_scdd[idxno]
    if salesamt > 0:
        sales.send(idxno, salesamt, acc.repay)
        
    #### Expected Costs: calculate expected costs ####
    # calculate operating costs
    _oprtg_cost = [_acc.add_scdd[idxno] for _acc in cost.lfkey("account")]
    oprtg_cost = sum(_oprtg_cost)
    
    _fncrsng_cost = [_acc.add_scdd[idxno] for _acc in fnccst.lfkey("account")]
    fncrsng_cost = sum(_fncrsng_cost)
    
    # calculate financial costs
    for rnk in loan.rnk:
        if idxno == loan[rnk].idxfn[0]:
            loan[rnk].fee.addscdd(idxno, loan[rnk].fee.amt)
        if all([loan[rnk].is_wtdrbl, not loan[rnk].is_repaid]):
            loan[rnk].IR.addscdd(idxno, loan[rnk].IRamt_topay(idxno))
    
    # gathering financial costs
    fncl_fee = loan.ttl.fee.add_scdd[idxno]
    fncl_IR = loan.ttl.IR.add_scdd[idxno]

    cost_ttl = oprtg_cost + fncrsng_cost + fncl_fee + fncl_IR
        
    
    #### Loans: withdraw loan ####
    # calculate the amount to withdraw
    amt_rqrd = acc.oprtg.amt_rqrd_excess(idxno, cost_ttl)
    
    # withdraw loan amount
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

        
        
        
        
        
        
        
        
        
        
        
        
        
