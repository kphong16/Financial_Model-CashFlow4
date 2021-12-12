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

import cafle as cf
from cafle.genfunc import rounding as R
from cafle.genfunc import PY
from cafle.genfunc import EmptyClass
from cafle.genfunc import read_json


#### Initial Setting ####
CASE = "case2"
astn = EmptyClass()


#### Read Financing Condition Data ####
with open(f'{CASE}/astn_financing.txt', 'r') as f:
    astn.fnc = json.load(f)
    astn.index = astn.fnc['index']
    astn.equity = astn.fnc['equity']
    astn.loan = astn.fnc['loan']
    
idx = cf.PrjtIndex(idxname = astn.index['idxname'],
                   start   = astn.index['start'],
                   periods = astn.index['periods'],
                   freq    = astn.index['freq'])
                   
equity = cf.Loan(idx,
                 amt_ntnl = astn.equity["amt_ntnl"],
                 amt_intl = astn.equity["amt_ntnl"])
                 
loan = cf.Intlz_loan(idx, idx.loan,
                     title    = astn.loan["title"],
                     rnk      = astn.loan["rnk"],
                     amt_ntnl = astn.loan["amt_ntnl"],
                     amt_intl = astn.loan["amt_intl"],
                     rate_fee = astn.loan["rate_fee"],
                     rate_IR  = astn.loan["rate_IR"])


#### Read Sales Data ####
with open(f"{CASE}/astn_sales.txt", "r") as f:
    astn.sales = json.load(f)
    
sales = cf.Account(idx, 'Sales')
sales.addamt(idx.sales[0], astn.sales['amount'])
sales.subscdd(idx.sales[-1], astn.sales['amount'])


#### Read Cost Data and Create Cost Accounts ####
cost = cf.Collect(idx, adrs_json=f"{CASE}/astn_cost.txt")

# Additional add schedule
if cost["tax_aqstn"]["additional_addscdd"] == True:
    tmp_rate = cost["tax_aqstn"]["취득세율"] + \
               cost["tax_aqstn"]["농특세율"] + \
               cost["tax_aqstn"]["교육세율"]
    tmp_amt = cost["prchs"]["amt"] * tmp_rate
    tmp_idx = idx.loan[0]
    cost.acc("tax_aqstn").addscdd(tmp_idx, tmp_amt)
    cost["tax_aqstn"]["additional_addscdd"] = False


#### Read Operating Accounts Data and Create ####
acc = cf.Collect(idx, adrs_json=f"{CASE}/astn_account.txt")


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
        sales.send(idxno, salesamt, acc.acc("repay"))
        
    #### Expected Costs: calculate expected costs ####
    # calculate operating costs
    _oprtg_cost = [_acc.add_scdd[idxno] for _acc in cost.lfkey("account")]
    oprtg_cost = sum(_oprtg_cost)
        
    # calculate financial costs
    for rnk in loan.rnk:
        if idxno == loan[rnk].idxfn[0]:
            loan[rnk].fee.addscdd(idxno, loan[rnk].fee.amt)
        if all([loan[rnk].is_wtdrbl, not loan[rnk].is_repaid]):
            loan[rnk].IR.addscdd(idxno, loan[rnk].IRamt_topay(idxno))
    
    # gathering financial costs
    fncl_fee = loan.ttl.fee.add_scdd[idxno]
    fncl_IR = loan.ttl.IR.add_scdd[idxno]

    cost_ttl = oprtg_cost + fncl_fee + fncl_IR
        
    
    #### Loans: withdraw loan ####
    # calculate the amount to withdraw
    amt_rqrd = acc.acc("oprtg").amt_rqrd_excess(idxno, cost_ttl)
    
    # withdraw loan amount
    amt_wtdrw = 0
    amt_wtdrw += equity.wtdrw(idxno, equity.amt_intl, acc.acc("oprtg"))
    if idxno == idx.loan[0]:
        # withdraw initial loan amount
        for rnk in sorted(loan.rnk, reverse=True):
            amt_wtdrw += loan[rnk].wtdrw(idxno, loan[rnk].amt_intl, acc.acc("oprtg"))
    
    amt_rqrd = max(amt_rqrd - amt_wtdrw, 0)
    for rnk in sorted(loan.rnk, reverse=True):
        amt_rqrd = max(amt_rqrd - loan[rnk].wtdrw(idxno, amt_rqrd, acc.acc("oprtg")), 0)
        
    
    #### Costs: 토지비, 공사비 등 각종 비용 지출 ####
    lst_cst = cost.lfkey("account")
    for cst in lst_cst:
        amt_scdd = cst.add_scdd[idxno]
        acc.acc("oprtg").send(idxno, amt_scdd, cst)
        
        
    #### Loans: pay financial cost ####
    for rnk in loan.rnk:
        acc.acc("oprtg").send(idxno, loan[rnk].fee.add_scdd[idxno], loan[rnk].fee)
        
    for rnk in loan.rnk:
        acc.acc("oprtg").send(idxno, loan[rnk].IR.add_scdd[idxno], loan[rnk].IR)
        
        
    #### Loans: repay loan amount ####
    if idxno >= loan.idxfn[-1]: # 만기 도래 여부 확인
        for rnk in loan.rnk:
            if rnk == 0 or loan[rnk-1].is_repaid:
                amtrpy = loan[rnk].repay_amt(idxno, acc.acc("repay").bal_end[idxno])
                acc.acc("repay").send(idxno, amtrpy, loan[rnk].ntnl)
                loan[rnk].set_repaid(idxno)
        
            if rnk == max(loan.rnk):
                acc.acc("repay").send(idxno, acc.acc("repay").bal_end[idxno], acc.acc("oprtg"))
        
    
    #### Loans: Set back loan unwithdrawble at maturity ####
    # If it was maturity date then set back loan unwithdrawble.
    equity.setback_wtdrbl_mtrt(idxno)
    for rnk in loan.rnk:
        loan[rnk].setback_wtdrbl_mtrt(idxno)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
