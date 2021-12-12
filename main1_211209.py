#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 22:38:10 2021

@author: KP_Hong
"""

import pickle
import pandas as pd
from pandas import Series, DataFrame
import numpy as np

import cafle as cf
from cafle.genfunc import rounding as R
from cafle.genfunc import PY
from cafle.genfunc import EmptyClass

pd.options.display.max_columns = 40
pd.options.display.max_rows = 200



#### Initial Setting ####
CASE = "case1"
astn = EmptyClass()



#### Area Data ####
# pickling data
with open("data/area.pickle", "rb") as fr:
    data_area = pickle.load(fr)
        
data_area['mtrxpy'].to_csv(f"{CASE}/area_py.csv")

# area data summary
area_ttl = data_area['mtrxpy'].loc[('ttl', 'sum'), ('ttl', 'sum')]

loc_cld = [x  in ['b1', 'f1'] for x in data_area['mtrxpy'].index.get_level_values(1)]
area_cld = sum(data_area['mtrxpy'].loc[:, ('ttl', 'sum')][loc_cld])

loc_nml = [x  in ['f2', 'f3', 'f4'] for x in data_area['mtrxpy'].index.get_level_values(1)]
area_nml = sum(data_area['mtrxpy'].loc[:, ('ttl', 'sum')][loc_nml])

floor_ttl = data_area['mtrxpy'].loc[('ttlfloor', 'sum'), ('ttl', 'sum')]

loc_cld = [x in ['b1', 'f1'] for x in data_area['mtrxpy'].loc['ttlfloor'].index]
floor_cld = sum(data_area['mtrxpy'].loc['ttlfloor'].loc[:, ('ttl', 'sum')][loc_cld])

loc_nml = [x in ['f2', 'f3', 'f4'] for x in data_area['mtrxpy'].loc['ttlfloor'].index]
floor_nml = sum(data_area['mtrxpy'].loc['ttlfloor'].loc[:, ('ttl', 'sum')][loc_nml])

rent_ttl = data_area['mtrxpy'].loc[('ttl', 'sum'), ('rent', 'sum')]

loc_cld = [x  in ['b1', 'f1'] for x in data_area['mtrxpy'].index.get_level_values(1)]
rent_cld = sum(data_area['mtrxpy'].loc[:, ('rent', 'sum')][loc_cld])

loc_nml = [x  in ['f2', 'f3', 'f4'] for x in data_area['mtrxpy'].index.get_level_values(1)]
rent_nml = sum(data_area['mtrxpy'].loc[:, ('rent', 'sum')][loc_nml])


with open(f"{CASE}/area_summary.txt", "w") as fr:
    fr.writelines(f"Total area  : {area_ttl:>10,.1f}\n")
    fr.writelines(f"Cold area   : {area_cld:>10,.1f}\n")
    fr.writelines(f"Nomal area  : {area_nml:>10,.1f}\n")
    fr.writelines(f"Total floor : {floor_ttl:>10,.1f}\n")
    fr.writelines(f"Cold floor  : {floor_cld:>10,.1f}\n")
    fr.writelines(f"Nomal floor : {floor_nml:>10,.1f}\n")
    fr.writelines(f"Total rent  : {rent_ttl:>10,.1f}\n")
    fr.writelines(f"Cold rent   : {rent_cld:>10,.1f}\n")
    fr.writelines(f"Nomal rent  : {rent_nml:>10,.1f}\n")
    


#### Input Index Data ####
astn.index = pd.read_csv(f'{CASE}/astn_index.csv')
idx = cf.PrjtIndex(idxname = list(astn.index.idxname),
                   start   = list(astn.index.start),
                   periods = list(astn.index.periods + 1),
                   freq    = 'M')



#### Input Financing Condition Data ####
astn.equity = pd.read_csv(f'{CASE}/astn_equity.csv')
equity = cf.Loan(idx,
                 amt_ntnl = astn.equity.amt_ntnl[0],
                 amt_intl = astn.equity.amt_intl[0])

astn.loan = pd.read_csv(f'{CASE}/astn_loan.csv')
loan = cf.Intlz_loan(idx, idx.loan,
                     title = astn.loan.title,
                     rnk = astn.loan.rnk,
                     amt_ntnl = astn.loan.amt_ntnl,
                     amt_intl = astn.loan.amt_intl,
                     rate_fee = astn.loan.rate_fee,
                     rate_IR = astn.loan.rate_IR)

astn.feeonbal = pd.read_csv(f'{CASE}/astn_feeonbal.csv', index_col='item')
loan.feeonbal_tra = astn.feeonbal.loc['feeonbal_tra'][0]

fee_amt = sum(astn.loan.amt_ntnl * astn.loan.rate_fee)
IR_amt = sum(astn.loan.amt_ntnl * astn.loan.rate_IR * 29 / 12)
arng_amt = sum(astn.loan.amt_ntnl * 0.02)

ttl_amt = fee_amt + IR_amt + arng_amt
allin_rate = ttl_amt / sum(astn.loan.amt_ntnl) * 12 / 29



#### Input Sales Data
sales_value = 125_000
sales = cf.Account(idx, 'Sales')
sales.addamt(idx.sales[0], sales_value)
sales.subscdd(idx.sales[-1], sales_value)



#### Input Cost Data
# set cost class
cost = cf.Cost(idx)

# land purchase costs
lnd = {}

title = ('lnd', 'prchs') # land purchase cost
byname = '용지매입비'
lnd['prchs'] = 14_500
tmp_ary = [[idx.prjt[0],  1_000],
           [idx.loan[0], 13_500]]
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('lnd', 'brkrg') # land brokerage fee
byname = '부동산중개비용'
lnd['brkrg'] = lnd['prchs'] * 0.009
intlcst = 39
tmp_ary = [[idx.prjt[0],  intlcst],
           [idx.loan[0],  lnd['brkrg'] - intlcst]]
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('lnd', 'nhbond') # national housing bond
byname = '국민주택채권'
매입률 = 0.045
본인부담률 = 0.055
lnd['nhbond'] = lnd['prchs'] * 매입률 * 본인부담률
tmp_ary = [[idx.loan[0], lnd['nhbond']]]
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('lnd', 'jdclcst') # judicial scrivener cost
byname = '법무사비용'
수수료율 = 0.001
lnd['jdclcst'] = lnd['prchs'] * 수수료율
tmp_ary = [[idx.loan[0], lnd['jdclcst']]]
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('lnd', 'tax_aqstn') # land acquisition and registration tax
byname = '취등록세'
취득세율 = 0.040
농특세율 = 0.002
교육세율 = 0.004
lnd['tax_aqstn'] = sum(cost['lnd'].amt) * (취득세율 + 농특세율 + 교육세율)
tmp_ary = [[idx.loan[0], lnd['tax_aqstn']]]
cost.inptcst(title, byname, scdddf=tmp_ary)


lnd['sum'] = sum(cost['lnd'].amt)


# construction costs
cstrn = {}
cstrn['dmltn'] = 35 + 1_180 # 철거비: 3,550평 x 342천원
cstrn['civil'] = 8_490 # 토목공사: 16,327평 x 520천원
cstrn['nml_fclt'] = area_nml * 2.66 # 상온시설: 9,311평 x 2,660천원
cstrn['cld_fclt'] = area_cld * 3.66 # 저온시설: 8,365평 x 3,660천원
cstrn['ttl_fclt'] = cstrn['nml_fclt'] + cstrn['cld_fclt']

cstrn['sum'] = 65_000 # 철거, 토목, 건축공사 통합 650억원으로 설정

retention_rate = 0.1
cstrn['intl'] = 35
cstrn['sum_prd'] = cstrn['sum'] * (1-retention_rate) - cstrn['intl']
cstrn['sum_rttn'] = cstrn['sum'] * retention_rate

title = ('cstrn', 'cstrn') # construction cost
byname = '공사비'
tmp_idx = idx.cstrn.index
tmp_len = len(idx.cstrn)
tmp_ary = [[idx.prjt[0], cstrn['intl']]]
tmp_ary.extend([[x, cstrn['sum_prd'] / tmp_len] for x in tmp_idx])
tmp_ary.append([idx.prjt[-1], cstrn['sum_rttn']])

cost.inptcst(title, byname, scdddf=tmp_ary)


# indirect construction costs
cstrnidrt = {}

title = ('cstrnidrt', 'wtrelec') # water supply, electricity etc. 
byname = '각종인입비'
cstrnidrt['wtrelec'] = 980
tmp_ary = [[idx.locval(2023, 10), cstrnidrt['wtrelec']]]
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('cstrnidrt', 'wsctbn') # water and sewage contribution
byname = '상수도분담금'
cstrnidrt['wsctbn'] = 163
tmp_ary = [[idx.locval(2023, 10), cstrnidrt['wsctbn']]]
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('cstrnidrt', 'dsgncst') # design cost
byname = '설계비'
cstrnidrt['dsgncst'] = 624
tmp_ary = [[idx.loan[0], cstrnidrt['dsgncst']]]
# 16,327평 x 38천원
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('cstrnidrt', 'lcnscst') # license cost
byname = '인허가비용'
cstrnidrt['lcnscst'] = 528
tmp_ary = [[idx.loan[0], cstrnidrt['lcnscst']]]
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('cstrnidrt', 'spvsn') # supervision cost
byname = '감리비'
cstrnidrt['spvsn'] = 490 # 16,327평 x 30천원, 월별 분할 부과
tmp_idx = idx.cstrn.index
tmp_len = len(idx.cstrn)
tmp_ary = [[x, cstrnidrt['spvsn'] / tmp_len] for x in tmp_idx]
cost.inptcst(title, byname, scdddf=tmp_ary)


# marketing costs
mrktg = {}

title = ('mrktg', 'rentagncy') # rent agency cost
byname = '임대대행수수료'
mrktg['rentagncy'] = 1_115
tmp_ary = [[idx.prjt[-1], mrktg['rentagncy']]]
# 임대계약 실행시 월 임대료의 2개월치 지급
# 1개월치 임대료 517백만원 가정
# 전액 성공불 지급
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('mrktg', 'salescsltg') # sales consulting fee
byname = '매각컨설팅수수료'
mrktg['salescsltg'] = 1_000
tmp_ary = [[idx.loan[0], mrktg['salescsltg']]]
# 추정매각가 x 0.8%
# 전액 성공불 지급
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('mrktg', 'advtsmnt') # advertisement and promotion cost
byname = '광고홍보비'
mrktg['advtsmnt'] = 500
tmp_ary = [[idx.locval(2022, 6), mrktg['advtsmnt'] * 0.5],
           [idx.locval(2023, 6), mrktg['advtsmnt'] * 0.5]]
cost.inptcst(title, byname, scdddf=tmp_ary)


# tax and utility bills(제세공과금)
title = ('taxutlt', 'prpttax') # property tax
byname = '재산세종부세'
tmp_ary = [[idx.locval(2022, 6), 37],
           [idx.locval(2023, 6), 37]]
# 5,590 x 0.62% 2년
cost.inptcst(title, byname, scdddf=tmp_ary)


title = ('taxutlt', 'prsvtntax') # preservation registration fee
byname = '보존등기비'
tmp_ary = [[idx.cstrn[-1], 2_866]]
# 건물 취득비용 x 3.40%(취득세 2.8%, 농특세 0.2%, 교육세 0.16%, 법무사 0.24%)
cost.inptcst(title, byname, scdddf=tmp_ary)


# Additional Costs
title = ('addtnl', 'pmfee') # Additional expense, PM fee
byname = 'PM수수료'
tmp_ary = [[idx.loan[0], 200]]
cost.inptcst(title, byname, scdddf=tmp_ary)

title = ('addtnl', 'oprtgcst') # company operating cost
byname = '운영비'
unt_amt = 30 # 3,000만원/월
tmp_idx = idx.loan.index
tmp_ary = [[x, unt_amt] for x in tmp_idx]
cost.inptcst(title, byname, scdddf=tmp_ary)

title = ('addtnl', 'rsrvfund') # reserve fund
byname = '예비비'
tmp_ary = [[idx.locval(2022, 6), 940],
           [idx.locval(2023, 6), 939]]
cost.inptcst(title, byname, scdddf=tmp_ary)

title = ('addtnl', 'trustcst') # trust fee
byname = '신탁수수료'
tmp_ary = [[idx.loan[0], 1_879]]
cost.inptcst(title, byname, scdddf=tmp_ary)

title = ('addtnl', 'csltcst') # consulting fee
byname = '사평감평용역비'
tmp_ary = [[idx.prjt[0], 10],
           [idx.loan[0], 140]]
cost.inptcst(title, byname, scdddf=tmp_ary)

title = ('addtnl', 'legalcst') # legal advice fee
byname = '법률자문'
tmp_ary = [[idx.loan[0], 40]]
cost.inptcst(title, byname, scdddf=tmp_ary)


# Financing Costs
title = ('fncg', 'arngmnt') # financing arrangement fee
byname = '금융주관수수료'
tmp_rate = 0.02 #2.0%
tmp_amt = sum(loan.amt_ntnl)
tmp_ary = [[idx.loan[0], tmp_amt * tmp_rate]]
cost.inptcst(title, byname, scdddf=tmp_ary)

title = ('fncg', 'spcoprtg') # spc operating cost
byname = 'SPC유동화비용'
tmp_ary = [[idx.loan[0], 66]]
cost.inptcst(title, byname, scdddf=tmp_ary)

title = ('fncg', 'agntbank') # agent banking fee
byname = '대리금융기관'
tmp_ary = [[idx.locval(2022, 1), 30],
           [idx.locval(2023, 1), 30]]
cost.inptcst(title, byname, scdddf=tmp_ary)


# Cost Matrix
cost_dct = cost["all"].dct.items()
cost_df = DataFrame({key:item.add_scdd[:] for key, item in cost_dct})
cost_df[("sum", "sum")] = cost["all"].add_scdd[:]
cost_df.to_csv(f"{CASE}/cost_summary.csv")



#### Execution Cash Flow
acc = cf.Intlz_accounts(idx, ['oprtg', 'sales', 'repay'])

# Execute cash flow
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
    oprtg_cost = cost['all'].add_scdd[idxno]

    # calculate financial costs
    for rnk in loan.rnk:
        if idxno == loan[rnk].idxfn[0]:
            loan[rnk].fee.addscdd(idxno, loan[rnk].fee.amt)
        if all([loan[rnk].is_wtdrbl, not loan[rnk].is_repaid]):
            loan[rnk].IR.addscdd(idxno, loan[rnk].IRamt_topay(idxno))
    
    # calculate financial fee on balance on Tr.A
    ntnl_sub_rsdl_tra = loan.tra.ntnl_sub_rsdl(idxno)
    feeonbal = ntnl_sub_rsdl_tra * loan.feeonbal_tra / 12
    loan.tra.fee.addscdd(idxno, feeonbal)
    
    # gathering financial costs
    fncl_fee = loan.ttl.fee.add_scdd[idxno]
    fncl_IR = loan.ttl.IR.add_scdd[idxno]

    cost_ttl = oprtg_cost + fncl_fee + fncl_IR
    
    
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
    for cst_name, cst_acc in cost['all'].dct.items():
        amt_scdd = cst_acc.add_scdd[idxno]
        acc.oprtg.send(idxno, amt_scdd, cst_acc)
        
    
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






