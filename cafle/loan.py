import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd
import datetime as dt
from datetime import datetime
from datetime import timedelta
from datetime import date
from functools import wraps

# import 
# from ingenfuncdex import Index
# from account import Account, Merge
from .genfunc import *
from .index import Index, PrjtIndex
from .account import Account, Merge

__all__ = ['Loan', 'Merge_loan', 'Intlz_loan']

class Loan(object):
    """
    PARAMETERS
    - index : basic index class
    - idxfn : financial index class
    - amt_ntnl : notional amount, float
    - rate_fee : initial fee rate, float
    - rate_IR : interest rate, float
    - IRcycle : interest payment cycle(months), int
    - title : name of loan, str
    - tag : tags of loan, tuple of str
    - note : note, str
    ATTRIBUTES
    - cindex / cidxfn : index class instance
    - index / idxfn : index data of index class instance
    - is_wtdrbl : boolean(True or False), whether it's withdrawable or not.
                  default false
    - is_repaid : boolean(True or False), whether it's repaid or not.
                  default false
    - ntnl : Account instance of notional amount
    - fee : Account instance of fee amount
    - IR : Account instance of IR amount
    - dctmrg : Merge of dictionary ntnl, fee, IR.
    - _df : _df of dctmrg
    - df : df of dctmrg
    METHODS
    - set_wtdrbl_intldate(date) : If the date is an initial date, then set is_wtdrbl True
    - setback_wtdrbl_mtrt(date) : If the date is a maturity date, then set back is_wtdrbl False
    - set_wtdrbl_false() : set is_wtdrbl False
    - set_repaid() : After check that notional amount is repaid, set is_repaid True.
    """
    def __init__(self,
                 index, # basic index class
                 idxfn = None, # financial index class
                 amt_ntnl = 0, # float
                 amt_intl = None,
                 rate_fee = 0.0, # float
                 rate_IR = 0.0, # float
                 rate_fob = 0.0, # float
                 IRcycle = 1, # int, months
                 title = None, # string : "LoanA"
                 rnk = 0, # int
                 tag = None, # string tuple : ("tagA", "tagB")
                 note = "" # string
                 ):
        if idxfn == None:
            idxfn = index
        
        # index 입력
        if isinstance(index, Index):
            self.cindex = index
            self.index = index.index
        elif isinstance(index, PrjtIndex):
            self.cindex = index._prjt
            self.index = index.index
        
        # idxfn 입력
        if isinstance(idxfn, Index):
            self.cidxfn = idxfn
            self.idxfn = idxfn.index
        elif isinstance(index, PrjtIndex):
            self.cidxfn = idxfn._prjt
            self.idxfn = idxfn.index
            
        # 주요 변수 입력
        self.amt_ntnl = amt_ntnl
        self.amt_intl = amt_intl
        self.rate_fee = rate_fee
        self.rate_IR = rate_IR
        self.rate_fob = rate_fob
        self.IRcycle = IRcycle
        self._rate_IR_cycle = rate_IR * self.IRcycle / 12
        self._rate_fob_cycle = rate_fob * self.IRcycle / 12
            
        # title, rank 입력
        self.title = title
        self.rnk = rnk
        
        # tag 입력 : tag는 튜플로 받음. string으로 입력된 경우 튜플로 변환 필요
        if isinstance(tag, tuple):
            self.tag = tag
        elif isinstance(tag, str):
            self.tag = tuple(tag)
        elif tag is None:
            self.tag = None
        else:
            raise ValueError("tag is not a tuple")
            
        # note 입력
        self.note = note
        
        # is withdrawable, repaid
        self._is_wtdrbl = False
        self._is_repaid = False
        
        # Account Setting
        self.ntnl = Account(self.cindex, self.title, self.tag)
        self.fee = Account(self.cindex, self.title, self.tag)
        self.IR = Account(self.cindex, self.title, self.tag)
        self.fob = Account(self.cindex, self.title, self.tag)
        
        # Initialize
        self.dct = {}
        self._intlz()
        self.dctmrg = Merge(self.dct)
    
    def __getattr__(self, attr):
        """
        기존에 정의되어 있지 않은 속성이 입력될 경우, Account 객체를 조회하여 속성
        존재 여부를 확인함.
        """
        return [dctval.__dict__[attr] for dctval in self.dct.values()]
        
    def _intlz(self):
        # 초기화 함수 실행    
        self.ntnl.amt = self.amt_ntnl
        self.ntnl.subscdd(self.cidxfn.index[0], self.ntnl.amt)
        self.ntnl.addscdd(self.cidxfn.index[-1], self.ntnl.amt)
        self.dct['ntnl'] = self.ntnl
        
        self.fee.rate = self.rate_fee
        self.fee.amt = self.ntnl.amt * self.fee.rate
        self.dct['fee'] = self.fee
        
        self.IR.rate = self.rate_IR
        self.IR.rate_cycle = self._rate_IR_cycle
        self.IR.amt_cycle = self.ntnl.amt * self.IR.rate_cycle
        self.dct['IR'] = self.IR
        
        self.fob.rate = self.rate_fob
        self.fob.rate_cycle = self._rate_fob_cycle
        self.dct['fob'] = self.fob
        
    @property
    def _df(self):
        return self.dctmrg._df
        
    @property
    def df(self):
        return self.dctmrg.df
    
    
    #### set loan withdrawable ####
    @property
    def is_wtdrbl(self):
        return self._is_wtdrbl
    @is_wtdrbl.setter
    def is_wtdrbl(self, value):
        self._is_wtdrbl = value
    
    def set_wtdrbl_intldate(self, date, critdate=None):
        """If the date is an initial date, then set is_wtdrbl True"""
        if critdate:
            tmp_crit = critdate
        else:
            tmp_crit = self.idxfn[0]
        if date == tmp_crit:
            self.is_wtdrbl = True
    
    def setback_wtdrbl_mtrt(self, date):
        """If the date is a maturity date, then set back is_wtdrbl False"""
        if date == self.idxfn[-1]:
            self.set_wtdrbl_false()
            
    def set_wtdrbl_false(self):
        """Set is_wtdrbl False"""
        self.is_wtdrbl = False
    #### set loan withdrawable ####
    
    
    #### set loan repaid all ####
    @property
    def is_repaid(self):
        return self._is_repaid
    @is_repaid.setter
    def is_repaid(self, value):
        self._is_repaid = value
        
    def set_repaid(self, date):
        if self.is_wtdrbl == False:
            return
        if -self.ntnl.bal_end[date] > 0:
            return
        if (self.ntnl.sub_rsdl_cum[date] - self.ntnl.add_rsdl_cum[date]) > 0:
            return
        self.is_repaid = True
    #### set loan repaid all ####
    
    
    #### calculate IR amount to pay ####
    def IRamt_topay(self, idxno):
        tmp_ntnl = -self.ntnl.bal_strt[idxno]
        tmp_IRamt = tmp_ntnl * self.IR.rate_cycle
        return tmp_IRamt
        
    def fobamt_topay(self, idxno):
        tmp_ntnl = self.ntnl_sub_rsdl(idxno)
        tmp_fobamt = tmp_ntnl * self.fob.rate_cycle
        return tmp_fobamt
    #### calculate IR amount to pay ####
    
    
    #### withdraw loan ####
    def wtdrw(self, idxno, amt, acc):
        """ idxno에 대응하는 누적인출가능잔액 확인.
        누적인출가능잔액 내에서 인출필요금액을 계좌로 이체
        """
        if not self.is_wtdrbl:
            return 0
        if self.is_repaid:
            return 0
            
        ntnl_sub_rsdl = self.ntnl.sub_rsdl_cum[idxno] # 누적 인출 가능 대출원금
        tmp_wtdrw = limited(amt,
                            upper=[ntnl_sub_rsdl],
                            lower=[0])
        if tmp_wtdrw > 0:
            self.ntnl.send(idxno, tmp_wtdrw, acc)
        return tmp_wtdrw
    #### withdraw loan ####
    
    
    #### repayment ####
    def ntnl_bal_end(self, idxno):
        """미상환 대출원금 잔액"""
        return -self.ntnl.bal_end[idxno]
        
    def amt_rpy_exptd(self, idxno):
        """상환 기일이 도래한 대출원금"""
        rpy_amt = limited(self.ntnl.add_rsdl_cum[idxno],
                          upper=[self.ntnl_bal_end(idxno)],
                          lower=[0])
        return rpy_amt
        
    def ntnl_sub_rsdl(self, idxno):
        """잔여 대출 한도"""
        amt_rsdl = limited(self.ntnl.sub_rsdl_cum[idxno],
                           lower=[0])
        return amt_rsdl
    
    def repay_amt(self, idxno, amtrpy):
        """미상환 대출원금 잔액 한도 내 상환금액 계산"""
        tmprpy = limited(amtrpy, 
                         upper=[self.ntnl_bal_end(idxno)],
                         lower=[0])
        return tmprpy
    #### repayment ####
    #####################################################
    # fee 입금 함수, IR 입금 함수, ntnl 출금, 입금 함수 추가 필요 #


class Merge_loan(Merge):
    @property
    def ntnl(self):
        tmp_dct = {key:val.ntnl for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
    
    @property
    def fee(self):
        tmp_dct = {key:val.fee for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
        
    @property
    def IR(self):
        tmp_dct = {key:val.IR for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc
        
    @property
    def fob(self):
        tmp_dct = {key:val.fob for key, val in self.dct.items()}
        rslt_acc = Merge(tmp_dct)
        return rslt_acc    
    
    @property
    def is_repaid(self):
        tmp_rslt = all([val.is_repaid for val in self.dct.values()])
        return tmp_rslt
      
        
class Intlz_loan:
    def __init__(self,
                 index, # basic index class
                 idxfn = None, # financial index class
                 title = [], # list, loan name
                 rnk = [], # list, loan rank
                 amt_ntnl = [], # list/float, loan notional amount
                 amt_intl = None,
                 rate_fee = [], # list/float
                 rate_IR = [], # list/float
                 rate_fob = [], # list/float, fee on balance
                 IRcycle = 1, # int or list / default 1, months
                 tag = None, # string tuple : ("tagA", "tagB")
                 note = "", # string
                 **kwargs
                 ):
        # index 입력
        self.index = index
        self.idxfn = idxfn        
            
        # 주요 변수 입력
        self.title = title
        self.rnk = rnk
        self.len = len(title)
        self.amt_ntnl = amt_ntnl
        self.amt_intl = amt_intl
        self.rate_fee = rate_fee
        self.rate_IR = rate_IR
        self.rate_fob = rate_fob
        
        if is_iterable(IRcycle):
            self.IRcycle = IRcycle
        elif isinstance(IRcycle, int):
            self.IRcycle = [IRcycle for _ in range(self.len)]
        
        self.tag = tag
        self.note = note
        self.kwargs = kwargs
        
        self.dct = {}
        self._intlz()
        
    def __len__(self):
        return self.len
    
    def _intlz(self):
        for i in range(self.len):
            tmpinstnc = Loan(index = self.index,
                             idxfn = self.idxfn,
                             amt_ntnl = self.amt_ntnl[i],
                             amt_intl = self.amt_intl[i],
                             rate_fee = self.rate_fee[i],
                             rate_IR = self.rate_IR[i],
                             rate_fob = self.rate_fob[i],
                             IRcycle = self.IRcycle[i],
                             title = self.title[i],
                             rnk = self.rnk[i],
                             tag = self.tag,
                             note = self.note
                             )
            for key, item in self.kwargs.items():
                setattr(tmpinstnc, key, item[i])
            self.dct[self.title[i]] = tmpinstnc
            setattr(self, self.title[i], tmpinstnc)
        
        self.ttl = Merge_loan(self.dct)
        for i in range(self.len):
            setattr(self.ttl, self.title[i], getattr(self, self.title[i]))
            
    def __getitem__(self, val):
        if type(val) is int:
            for key, item in self.dct.items():
                if item.rnk == val:
                    return item
        if type(val) is str:
            return getattr(self, val)