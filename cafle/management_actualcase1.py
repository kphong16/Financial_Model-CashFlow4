import pandas as pd
import numpy as np
import math
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd

from .genfunc import *
from .index import *
from .account import *

__all__ = ['Intlz_sales_sellinlots', 'Intlz_costs', 'Intlz_accounts',
           'Mngmnt_sls', 'Mngmnt_wtdrw', 'Mngmnt_cst', 'Mngmnt_repay']
           

class Intlz_sales_sellinlots:
    def __init__(self,
                 index, # basic index class
                 idxsls = None, # financial index class
                 slsmtrx = None, # sales matrix
                 slsctrt = None, # sales contract schedule
                 slscsh = None, # sales cash schedule on each contract
                 ):
        # index 입력
        self.index = index
        if idxsls == None:
            idxsls = index
        self.idxsls = idxsls
        
        # 주요 변수 입력
        self.slsmtrx = slsmtrx
        self.prdtlst = list(self.slsmtrx.index)
        self.slsctrt = slsctrt
        self.slscsh = slscsh
        
        self.dct = {}
        self._intlz()
        
    def _intlz(self):
        for no, prdt in enumerate(self.prdtlst):
            tmp_acc = Account(self.index)
            self.dct[prdt] = tmp_acc
            setattr(self, prdt, tmp_acc)
            
            # input sales matrix data on account
            for colname in self.slsmtrx.columns:
                setattr(self.dct[prdt], colname, getattr(self.slsmtrx, colname)[prdt])
            
            # input sales contract, cash data on account
            setattr(self.dct[prdt], 'ctrt', self.slsctrt[prdt])
            setattr(self.dct[prdt], 'csh', self.slscsh)
            
        self.ttl = Merge(self.dct)
        for no, prdt in enumerate(self.prdtlst):
            setattr(self.ttl, prdt, self.dct[prdt])
            
         
# Intializing Costs
class Intlz_costs:
    def __init__(self,
                 index, # basic index class
                 idxcst = None, # cost index class
                 ):
        # Input index
        self.index = index
        if idxcst == None:
            idxcst = index
        self.idxcst = idxcst
        
        self.title = []
        
        self.dct = {}
        self._intlz()
    
    def __len__(self):
        return len(self.title)
        
    def _intlz(self):
        pass
    
    def inptcst(self,
                title, # str
                scddidx, # list
                scddamt, # list
                **kwargs):
        if title not in self.title:
            self.title.append(title)
            tmp_acc = Account(self.index)
            self.dct[title] = tmp_acc
            setattr(self, title, tmp_acc)
        
        tmp_istnc = getattr(self, title)
        tmp_istnc.addscdd(scddidx, scddamt)
        
        setattr(tmp_istnc, 'amt', tmp_istnc.add_scdd[:].sum())
        
        for key, val in kwargs.items():
            setattr(tmp_istnc, key, val)
    
    @property
    def ttl(self):
        tmp_ttl = Merge(self.dct)
        for i, key in enumerate(self.title):
            setattr(tmp_ttl, key, getattr(self, key))
        return tmp_ttl
         
            
# Setting Accounts
class Intlz_accounts:
    def __init__(self,
                 index, # index
                 accname, # list/str
                 ):
        self.index = index
        self.accname = accname
    
        self.dct = {}
        self._intlz()
    
    def __len__(self):
        return len(self.accname)
    
    def _intlz(self):
        for no, accname in enumerate(self.accname):
            tmp_acc = Account(self.index)
            self.dct[accname] = tmp_acc
            setattr(self, accname, tmp_acc)
            
        self.ttl = Merge(self.dct)
        for no, accname in enumerate(self.accname):
            setattr(self.ttl, accname, getattr(self, accname))
            
            
# Receive sales amount
class Mngmnt_sls:
    def __init__(self, idxno, sales):
        self.idxno = idxno
        self.sls = sales
        
    # Check sales plan and input sales data
    def make_ctrt_plan(self):
        try:
            # check sales plan
            sls_amt = self.sls.ctrt.amt.loc[self.idxno]
            sls_odr = self.sls.ctrt.odr.loc[self.idxno]
            try:
                # input sales amount on this index no.
                self.sls.addscdd(self.idxno, sls_amt)
                self.sls.addamt(self.idxno, sls_amt)
            
                # input sales cash schedule on sales cash index.
                sls_csh = self.sls.csh[sls_odr]
                csh_idx = [max(self.idxno, x[0]) for x in sls_csh]
                csh_amt = [sls_amt * x[1] for x in sls_csh]
                self.sls.subscdd(csh_idx, csh_amt)
            except AttributeError as err:
                print("AttributeError", err)
        except:
            pass
        
    # Receive sales amount on sales account
    def rcv_slsamt(self, acnt_sales):
        sls_amt = self.sls.sub_rsdl_cum[self.idxno]
        self.sls.send(self.idxno, sls_amt, acnt_sales)


# Manage cost amount
class Mngmnt_cst:
    def __init__(self, idxno, cost):
        self.idxno = idxno
        self.cost = cost
    
    def _set_addscdd(self):
        pass
    
    @property
    def cst_oprtg(self):
        ttlsum = 0
        for cst_name, cst_acc in self.cost.dct.items():
            amt_scdd = cst_acc.add_scdd[self.idxno]
            ttlsum += amt_scdd
        return ttlsum
        
    def pay_oprtgcst(self, oprtg):
        """운영계좌에서 운영비용(operating cost) 지출"""
        for cst_name, cst_acc in self.cost.dct.items():
            amt_scdd = cst_acc.add_scdd[self.idxno]
            oprtg.send(self.idxno, amt_scdd, cst_acc)
            
    def cal_slsfee(self, sls_amt_ctrt):
        slsfee_amt = sls_amt_ctrt * self.cost.sales_fee.rate
        self.cost.sales_fee.addscdd(self.idxno, slsfee_amt)

        
# Calculate financial cost amount
class Mngmnt_fncl:
    def __init__(self, idxno, loan_each):
        self.idxno = idxno
        self.loan = loan_each
        
        self._scdd_fee()
        self._scdd_IR()
        
    def _scdd_fee(self):
        if self.idxno == self.loan.idxfn[0]:
            self.loan.fee.addscdd(self.idxno, self.loan.fee.amt)
            
    def _scdd_IR(self):
        if all([self.loan.is_wtdrbl, not self.loan.is_repaid]):
            tmp_ntnl = -self.loan.ntnl.bal_strt[self.idxno]
            tmp_IRamt = tmp_ntnl * self.loan.IR.rate_cycle
            self.loan.IR.addscdd(self.idxno, tmp_IRamt)
        
    @property
    def fee_scdd(self):
        return self.loan.fee.add_scdd[self.idxno]
        
    @property
    def IR_scdd(self):
        return self.loan.IR.add_scdd[self.idxno]
        
    @property
    def amt_scdd(self):
        return self.fee_scdd + self.IR_scdd
            
    def pay_fee(self, oprtg):
        oprtg.send(self.idxno, self.fee_scdd, self.loan.fee)
        
    def pay_IR(self, oprtg):
        oprtg.send(self.idxno, self.IR_scdd, self.loan.IR)
        
    def pay_all(self, oprtg):
        self.pay_fee(oprtg)
        self.pay_IR(oprtg)
            
            
# Withdraw loans.
class Mngmnt_wtdrw:
    def __init__(self, idxno, oprtg):
        self.idxno = idxno
        self.oprtg = oprtg
        
        self.amt_wtdrw = 0 # 인출된 금액
        self.rqrd_wtdrw = 0 # 인출 필요금액에 대한 인출 후 잔액
        
    def cal_amt_exptd(self, ttl_expense, minunit = 100):
        """총 지출필요금액(ttl_expense)에 대하여 운영계좌 잔액을 초과하는 금액
        (추가 인출이 필요한 금액)을 계산하여 class 속성에 대입"""
        bal_oprtg = self.oprtg.bal_end[self.idxno]
        
        amt_rqrd = max(ttl_expense - bal_oprtg, 0)
        amt_rqrd = round_up(amt_rqrd, -log10(minunit))
        # 지출필요금액에 대하여 운영계좌 잔액을 초과하는 금액 계산
        
        self.rqrd_wtdrw = amt_rqrd
            
    def wtdrw_eqty(self, eqty, amt_once=None):
        """equity instance에 대하여 idxno에 대응하는 인출예정금액(sub_scdd)을
        조회하여 운영계좌로 이체"""
        if all([eqty.is_wtdrbl, not eqty.is_repaid]):        
            amt_eqty = eqty.ntnl.sub_scdd[self.idxno]
            if amt_once:
                tmp_wtdrw = amt_once
            else:
                tmp_wtdrw = self.rqrd_wtdrw
            tmp_wtdrw = limited(tmp_wtdrw,
                                upper=[amt_eqty],
                                lower=[0])
            eqty.ntnl.send(self.idxno, tmp_wtdrw, self.oprtg)
            # 인출금액을 equity 계좌에서 oprtg 계좌로 이체
            self.amt_wtdrw += tmp_wtdrw
            self.rqrd_wtdrw -= tmp_wtdrw
    
    def wtdrw_loan(self, loan_each, amt_once=None):
        """loan instance에 대하여 idxno에 대응하는 누적인출가능잔액 확인,
        누적인출가능잔액 내에서 인출필요금액(비용 등)을 운영계좌로 이체"""
        loan = loan_each
        if all([loan.is_wtdrbl, not loan.is_repaid]):
            ntnl_sub_rsdl = loan.ntnl.sub_rsdl_cum[self.idxno] # 누적 인출가능 대출원금
            
            if amt_once:
                tmp_wtdrw = limited(amt_once,
                                    upper=[ntnl_sub_rsdl],
                                    lower=[0])
            else:
                tmp_wtdrw = limited(self.rqrd_wtdrw,
                                    upper=[ntnl_sub_rsdl],
                                    lower=[0])
            # 인출필요금액과 누적 인출가능 대출원금을 비교하여 적은 금액을 대입
            
            loan.ntnl.send(self.idxno, tmp_wtdrw, self.oprtg)
            # 인출금액을 loan 계좌에서 oprtg 계좌로 이체
            self.amt_wtdrw += tmp_wtdrw
            self.rqrd_wtdrw -= tmp_wtdrw
            
            
# Calculate expected repayment of loan and repay loan.
class Mngmnt_repay:
    def __init__(self, idxno, loan_each, oprtg, rpyacc):
        self.idxno = idxno
        self.loan = loan_each
        self.oprtg = oprtg
        self.rpyacc = rpyacc
    
    @property
    def ntnl_bal_end(self):
        """미상환 대출원금 잔액"""
        return -self.loan.ntnl.bal_end[self.idxno]
        
    @property
    def amt_rpy_exptd(self):
        """상환 기일이 도래한 대출원금"""
        rpy_amt = limited(self.loan.ntnl.add_rsdl_cum[self.idxno],
                          upper=[self.ntnl_bal_end],
                          lower=[0])
        return rpy_amt
                          
    @property
    def ntnl_sub_rsdl(self):
        """잔여 대출 한도"""
        amt_rsdl = limited(self.loan.ntnl.sub_rsdl_cum[self.idxno],
                           lower=[0])
        return amt_rsdl
                          
    def repayment_process(self):
        if self.idxno < self.loan.idxfn[-1]: # 만기 도래 여부 확인
            if self.ntnl_sub_rsdl > 0: # 잔여 대출 한도 확인
                # 운영계좌 이체 및 한도 차감
                amt_trsfr = limited(self.rpyacc.bal_end[self.idxno],
                                    upper=[self.ntnl_sub_rsdl],
                                    lower=[0])
                self.rpyacc.send(self.idxno, amt_trsfr, self.oprtg)
                self.loan.ntnl.subscdd(self.idxno, -amt_trsfr)
            if self.ntnl_sub_rsdl <= 0: # 잔여 대출 한도가 없는 경우
                self._repay_loan(self.rpyacc) # 대출금 상환
        elif self.idxno >= self.loan.idxfn[-1]: # 만기 도래 여부 확인
            self._repay_loan(self.rpyacc)
            self._repay_loan(self.oprtg)
            
    def _repay_loan(self, acc_to_rpy):
        amt_rpy = limited(acc_to_rpy.bal_end[self.idxno],
                          upper=[self.ntnl_bal_end],
                          lower=[0])
        acc_to_rpy.send(self.idxno, amt_rpy, self.loan.ntnl)
        self.loan.set_repaid(self.idxno)
                
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            