#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

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
    EmptyClass,
    )
from cafle.assumption import read_standard_process_rate_table
from .astn_financing import idx
from .astn_area import area
    

class Cost(Assumption_Base):
    def __init__(self, sales):
        super().__init__()
        self.sales = sales
        self._set_initial_data()
        
    def _set_initial_data(self):
        Account._index = idx.prjt
        self.key_main = []
        
        sgmnt = "lnd"
        self.key_main.append(sgmnt)
        
        title, byname   = "lndprchs", "토지매입비"
        acc             = self._set_account(title, byname, sgmnt)
        acc.area        = 9_074.4 #평
        acc.amt_ttl     = 14_704
        acc.note        = f"{acc.area:,.0f}평 x {acc.amt_ttl * 1000 / acc.area:,.0f}천원/평"
        acc.addscd(idx.loan[0], acc.amt_ttl)
        
        title, byname = "aqstntx", "취등록세"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    726)
        
        title, byname = "jdclscvn", "법무사"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     12)
        
        title, byname = "brkrg", "중개수수료"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    100)
        
        
        sgmnt = "cstrn"
        self.key_main.append(sgmnt)
        
        title, byname = "drtcstrn", "도급공사비"
        acc = self._set_account(title, byname, sgmnt)
        acc.amt_ttl     = 62_000 # 전층 상온 공사비
        acc.amt_prd     = 55_800
        acc.amt_rsrv    =  6_200
        acc.rate_rsrv   =   0.10
        acc.area_ttl    = 16_327
        acc.amt_unt     = acc.amt_prd / acc.area_ttl
        acc.prcrate     = read_standard_process_rate_table(len(idx.cstrn), tolist=True)
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note        = f"{acc.area_ttl:,.0f}평 x {acc.amt_unt*1000:,.0f}천원/평"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
            )
        acc.addscd(idx.cstrn[-1], acc.amt_rsrv)
        
        
        sgmnt = "adcstrn"
        self.key_main.append(sgmnt)
        
        title, byname = "rmvlcst", "철거비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],  1_215)
        
        title, byname = "rmvlspvsn", "철거감리비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     60)
        
        title, byname = "wtrelec", "인입비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    980)
        
        title, byname = "dsncst", "설계비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],  1_152)
        
        title, byname = "spvsncst", "감리비"
        acc = self._set_account(title, byname, sgmnt)
        acc.amt_unt = 82 # per month
        acc.amt_ttl = len(idx.cstrn) * acc.amt_unt
        acc.addscd(idx.cstrn,  [acc.amt_unt] * len(idx.cstrn))
        
        
        sgmnt = "consent" # construction consent
        self.key_main.append(sgmnt)
        
        title, byname = "cnsntcst", "인허가비용"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    528)
        
        title, byname = "treecst", "대체산림자원조성비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     48)
        
        title, byname = "farmland", "농지전용부담금"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     28)
        
        title, byname = "wtrswg", "상하수도원인자부담금"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    163)
        
        
        sgmnt = "slscst"
        self.key_main.append(sgmnt)
        
        title, byname = "rntbrkrg", "임대대행수수료"
        acc = self._set_account(title, byname, sgmnt)
        acc.rnt_unt   = self.sales.sales.rnt.rntamt.sum()
        acc.rnt_brcg_fee = acc.rnt_unt * 2
        acc.note    = f"월 임대료 {acc.rnt_unt:,.0f} x 2개월"
        acc.addscd(idx.cstrn[-1],acc.rnt_brcg_fee)#1_036)
        
        title, byname = "mrktgcst", "광고홍보비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    500)
        
        
        sgmnt = "oprtgcst"
        self.key_main.append(sgmnt)
        
        title, byname = "oprtgcpn", "시행사운영비"
        acc = self._set_account(title, byname, sgmnt)
        acc.amt_unt = 30
        acc.amt_ttl = len(idx.loan) * acc.amt_unt
        acc.note    = f"{acc.amt_unt*1000:,.0f}천원/월, {len(idx.loan)}개월"
        acc.addscd(idx.loan, [acc.amt_unt] * len(idx.loan))
        
        title, byname = "trustfee", "관리신탁수수료"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],  1_050)
        
        title, byname = "dptybnk", "대리금융기관수수료" #deputy banking fee
        acc = self._set_account(title, byname, sgmnt)
        acc.amt_unt = 30
        acc.amt_ttl = acc.amt_unt * 2
        acc.note    = f"{acc.amt_unt*1000:,.0f}천원, 2년"
        acc.addscd(idx.loan[0],     60)
        
        title, byname = "lawncstg", "법무/약정/사평/감평"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    190)
        
        title, byname = "prptytx", "재산세/종부세"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     75)
        
        title, byname = "pmfee", "PM수수료"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    200)
        
        title, byname = "rgstrtnfee", "보존등기비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.cstrn[-1],  2_456)
        
        title, byname = "rsrvfnd", "예비비"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    573)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        