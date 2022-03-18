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
from .astn_financing import idx
    

class Cost(Assumption_Base):
    def __init__(self):
        super().__init__()
        self._set_initial_data()
        
    def _set_initial_data(self):
        Account._index = idx.prjt
        
        title, byname, sgmnt = "lndprchs", "토지매입비", "lnd"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0], 14_704)
        
        title, byname, sgmnt = "aqstntx", "취등록세", "lnd"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    726)
        
        title, byname, sgmnt = "jdclscvn", "법무사", "lnd"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     12)
        
        title, byname, sgmnt = "brkrg", "중개수수료", "lnd"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    100)
        
        title, byname, sgmnt = "drtcstrn", "도급공사비", "cstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.amt_ttl =           66_700
        acc.amt_prd =           56_695
        acc.amt_rsrv =          10_005
        acc.rate_rsrv = 0.15
        acc.area_ttl = 16_327
        acc.amt_unt = acc.amt_prd / acc.area_ttl
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd / len(idx.cstrn)] * len(idx.cstrn)
            )
        acc.addscd(idx.cstrn[-1], acc.amt_rsrv)
        title, byname, sgmnt = "rmvlcst", "철거비", "adcstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],  1_215)
        
        title, byname, sgmnt = "rmvlspvsn", "철거감리비", "adcstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     60)
        
        title, byname, sgmnt = "wtrelec", "인입비", "adcstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    980)
        
        title, byname, sgmnt = "dsncst", "설계비", "adcstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],  1_152)
        
        title, byname, sgmnt = "spvsncst", "감리비", "adcstrn"
        acc = self._set_account(title, byname, sgmnt)
        acc.amt_unt = 82 # per month
        acc.amt_ttl = len(idx.cstrn) * acc.amt_unt
        acc.addscd(idx.cstrn,  [acc.amt_unt] * len(idx.cstrn))
        
        title, byname, sgmnt = "cnsntcst", "인허가비용", "consent" #construction consent
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    528)
        
        title, byname, sgmnt = "treecst", "대체산림자원조성비", "consent"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     48)
        
        title, byname, sgmnt = "farmland", "농지전용부담금", "consent"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     28)
        
        title, byname, sgmnt = "wtrswg", "상하수도원인자부담금", "consent"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    163)
        
        title, byname, sgmnt = "rntbrkrg", "임대대행수수료", "slscst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.cstrn[-1],1_036)
        
        title, byname, sgmnt = "mrktgcst", "광고홍보비", "slscst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    500)
        
        title, byname, sgmnt = "oprtgcpn", "시행사운영비", "oprtgcst"
        acc = self._set_account(title, byname, sgmnt)
        acc.amt_unt = 30
        acc.amt_ttl = len(idx.loan) * acc.amt_unt
        acc.addscd(idx.loan, [acc.amt_unt] * len(idx.loan))
        
        title, byname, sgmnt = "trustfee", "관리신탁수수료", "oprtgcst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],  1_050)
        
        title, byname, sgmnt = "dptybnk", "대리금융기관수수료", "oprtgcst" #deputy banking fee
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     60)
        
        title, byname, sgmnt = "lawncstg", "법무/약정/사평/감평", "oprtgcst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    190)
        
        title, byname, sgmnt = "prptytx", "재산세/종부세", "oprtgcst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],     75)
        
        title, byname, sgmnt = "pmfee", "PM수수료", "oprtgcst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    200)
        
        title, byname, sgmnt = "rgstrtnfee", "보존등기비", "oprtgcst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.cstrn[-1],  2_456)
        
        title, byname, sgmnt = "rsrvfnd", "예비비", "oprtgcst"
        acc = self._set_account(title, byname, sgmnt)
        acc.addscd(idx.loan[0],    573)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        