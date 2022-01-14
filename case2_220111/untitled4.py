#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 07:19:39 2022

@author: KP_Hong
"""

import pandas as pd
import numpy as np

from cafle2.index import (Index, PrjtIndex)
from cafle2.account import (Account, Merge)
from cafle2.loan import (Loan, Merge_loan, Intlz_loan)

idx = Index('2021-01', '2022-12')
pidx = PrjtIndex(['prjt', 'cstrn', 'loan'], 
                 ['2021-01', '2021-01', '2021-01'],
                 ['2022-12', '2022-12', '2022-12'])

acc = Account(pidx, "acc")
acc1 = Account(pidx, "acc1")
acc2 = Account(pidx, "acc2")
acc.subscd(idx[0], 10000)

mrg = Merge({'acc':acc, 'acc1':acc1, 'acc2':acc2})

ln = Loan("tra", pidx, pidx.loan, 10000, 0.05, rate_fee=0.01, rate_fob=0.005)
lnb = Loan("trb", pidx, pidx.loan, 50000, 0.07, rate_fee=0.02, rate_fob=0.005)
mrgln = Merge_loan({'tra':ln, 'trb':lnb})


lon = Intlz_loan(pidx, pidx.loan,
           title = ['tra', 'trb'],
           rnk = [0, 1],
           amt_ntnl = [50000, 40000],
           rate_IR = [0.05, 0.08],
           rate_fee = [0.01, 0.03],
           rate_arng = 0.02)