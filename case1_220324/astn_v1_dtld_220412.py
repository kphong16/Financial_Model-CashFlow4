"""
Created on 2022-03-30
@author: KP_Hong

Revised on 2022-04-12
Details of the holding tax were reflected.
"""

import os
from collections import namedtuple
import pandas as pd
from pandas import Series, DataFrame
import numpy as np

import cafle as cf
from cafle import (
    Account,
    Assumption_Base,
    Write,
    WriteWS,
    Cell,
)
from cafle.genfunc import (
    rounding as R,
    PY,
    Area,
    EmptyClass,
)
from cafle.assumption import read_standard_process_rate_table

#### Initial Setting ####
Name = namedtuple('Name', ['title', 'byname'])

#### Read Land Data ####
class LandMtrx(Assumption_Base):
    def __init__(self):
        super().__init__()

        DIRECTORY   = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        filename    = "/data/land.csv"
        fileloc     = DIRECTORY + filename

        self.rawdata = pd.read_csv(fileloc)
        self.rawdata['area_py'] = self.rawdata.area.apply(lambda x: Area(m2=x).py)

        self.ttl_area = sum(self.rawdata.area)
        self.ttl_areapy = sum(self.rawdata.area_py)
        self.ttl_value = sum(self.rawdata.value)
land = LandMtrx()

#### Read Area Data ####
class AreaMtrx(Assumption_Base):
    def __init__(self):
        super().__init__()

        DIRECTORY   = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        filename    = "/data/area.csv"
        fileloc     = DIRECTORY + filename

        self.rawdata = pd.read_csv(fileloc)
        self.rawdata['area_py'] = self.rawdata.area.apply(lambda x: Area(m2=x).py)

        self.mtrxd  = self._set_mtrx(valname='area')
        self.mtrx   = self._prt_mtrx(self.mtrxd)
        self.rent   = self.mtrxd['rent'].groupby(level=1).sum()

        self.mtrxpyd= self._set_mtrx(valname='area_py')
        self.mtrxpy = self._prt_mtrx(self.mtrxpyd)
        self.rentpy = self.mtrxpyd['rent'].groupby(level=1).sum()

        self.ttlfloor = self.mtrxpyd.loc["ttlfloor"]["ttl", "sum"].sum()
        self.lndpy  = 9_074.4 #평

    def _set_mtrx(self, valname='area'):
        _mtrx = self.rawdata.pivot_table(
            index   = ['ttlfloor', 'floor'],
            columns = ['exclsv',   'name' ],
            values  = valname,
            aggfunc = 'sum',
        )
        _mtrx[('ttl', 'sum')] = _mtrx.sum(axis=1)
        _mtrx[('exclsv', 'sum')] = _mtrx['exclsv'].sum(axis=1)
        _mtrx[('common', 'sum')] = _mtrx['common'].sum(axis=1)

        # Calculation rent area
        rent_col = ['berth', 'canopy', 'cldstrg', 'nmlstrg', 'office', 'stair']
        rent_col_share = ['mchnrm']

        rent_col_tpl = [('exclsv', x) for x in rent_col]
        rent_sum_tpl = _mtrx[rent_col_tpl].sum(axis=1)
        rent_share_tpl = sum([_mtrx[('exclsv', x)].sum() for x in rent_col_share])
        rent_share_tpl = rent_sum_tpl / rent_sum_tpl.sum() * rent_share_tpl
        _mtrx[('rent', 'sum')] = rent_sum_tpl + rent_share_tpl
        _mtrx = _mtrx.fillna(0)

        _mtrx = _mtrx[[
            ('exclsv', 'nmlstrg'),
            ('exclsv', 'cldstrg'),
            ('exclsv', 'canopy'),
            ('exclsv', 'berth'),
            ('exclsv', 'office'),
            ('exclsv', 'stair'),
            ('exclsv', 'mchnrm'),
            ('exclsv', 'sum'),
            ('common', 'passage'),
            ('common', 'ramp'),
            ('common', 'sum'),
            (   'ttl', 'sum'),
            (  'rent', 'sum')
        ]]
        _mtrx = _mtrx.reindex([
            ('ttlfloor', 'b1'),
            ('ttlfloor', 'f1'),
            ('ttlfloor', 'f2'),
            ('ttlfloor', 'f3'),
            ('ttlfloor', 'f4'),
            ('nonfloor', 'f1'),
            ('nonfloor', 'f3'),
        ])
        return _mtrx

    def _prt_mtrx(self, _mtrx):
        _mtrxsum            = _mtrx.sum(axis=0)
        _mtrxsum_ttlfloor   = _mtrx.loc['ttlfloor'].sum(axis=0)
        _mtrxsum_nonfloor   = _mtrx.loc['nonfloor'].sum(axis=0)

        _mtrxsum = DataFrame([_mtrxsum, _mtrxsum_ttlfloor, _mtrxsum_nonfloor],
                             index=[('ttl', 'sum'), ('ttlfloor', 'sum'), ('nonfloor', 'sum')],
                             columns=_mtrxsum.index)
        _mtrx = pd.concat([_mtrx, _mtrxsum])
        #_mtrx = _mtrx.append(_mtrxsum)
        _mtrx = _mtrx.fillna(0)

        _mtrx = _mtrx[[
            ('exclsv', 'nmlstrg'),
            ('exclsv', 'cldstrg'),
            ('exclsv', 'canopy'),
            ('exclsv', 'berth'),
            ('exclsv', 'office'),
            ('exclsv', 'stair'),
            ('exclsv', 'mchnrm'),
            ('exclsv', 'sum'),
            ('common', 'passage'),
            ('common', 'ramp'),
            ('common', 'sum'),
            ('ttl', 'sum'),
            ('rent', 'sum')]]
        _mtrx = _mtrx.reindex([
            ('ttlfloor', 'b1'),
            ('ttlfloor', 'f1'),
            ('ttlfloor', 'f2'),
            ('ttlfloor', 'f3'),
            ('ttlfloor', 'f4'),
            ('ttlfloor', 'sum'),
            ('nonfloor', 'f1'),
            ('nonfloor', 'f3'),
            ('nonfloor', 'sum'),
            ('ttl', 'sum'),
        ])

        _col = [
            ('전용', '상온'),
            ('전용', '저온'),
            ('전용', '캐노피'),
            ('전용', 'berth'),
            ('전용', '사무실'),
            ('전용', '계단'),
            ('전용', '기계실'),
            ('전용', '소계'),
            ('공용', '통로'),
            ('공용', '램프'),
            ('공용', '소계'),
            ('전체', '합계'),
            ('임대면적', '합계')]
        _idx = ([
            ('연면적', 'B1F'),
            ('연면적', '1F'),
            ('연면적', '2F'),
            ('연면적', '3F'),
            ('연면적', '4F'),
            ('연면적', '소계'),
            ('연면적제외', '1F'),
            ('연면적제외', '3F'),
            ('연면적제외', '소계'),
            ('전체', '합계'),
        ])
        _mtrx = DataFrame(_mtrx.values, _idx, _col)
        return _mtrx
area = AreaMtrx()

#### Assumption Index ####
class Idx:
    def __init__(self):
        self.prd_cstrn  = 22
        self.mtrt       = 28
        self.prd_fnc    = self.mtrt + 1
        self.prd_prjt   = self.mtrt + 4

        self.prjt       = cf.date_range("2022.03", periods=self.prd_prjt )
        self.loan       = cf.date_range("2022.04", periods=self.prd_fnc  )
        self.cstrn      = cf.date_range("2022.05", periods=self.prd_cstrn)
idx = Idx()

#### Assumption Financing ####
untamt = 1_000_000
class Equity:
    def __new__(cls):
        equity = cf.Loan(
            title       = "equity",
            index       = idx.prjt,
            amt_ntnl    = 1_500,
            amt_intl    = 1_500,
        ).this
        equity.ntnl.subscd(idx.prjt[0], equity.amt_ntnl)
        return equity
equity = Equity()

class Loan:
    def __new__(cls):
        loan = cf.Loan(
            index       = idx.prjt,
            idxfn       = idx.loan,

            mtrt        = idx.mtrt,
            rate_arng   = 0.02,
            title       = [  "tra",      "trb"],
            rnk         = [      0,          1],
            amt_ntnl    = [ 60_000,     36_000],
            amt_intl    = [      0,     36_000],
            rate_fee    = [  0.020,      0.020],
            rate_IR     = [  0.044,      0.080],
            rate_fob    = [  0.002,      0.000],
        )
        for key, item in loan.dct.items():
            item.ntnl.subscd(item.idxfn[0], item.amt_ntnl)
            item.ntnl.addscd(item.idxfn[-1], item.amt_ntnl)
        return loan
loan = Loan()

Account._index = idx.prjt
class LoanCst(Assumption_Base):
    def __init__(self, fnc_loan):
        super().__init__()
        self.fnc_loan = fnc_loan

        title, byname = "arngfee", "주관수수료"
        acc = self._set_account(title, byname)
        acc.addscd(
            idxval  = idx.loan[0],
            amt     = fnc_loan.amt_arng,
        )

        title, byname = "brdglncst", "브릿지론비용"
        acc = self._set_account(title, byname)
        acc.addscd(idx.loan[0], 540) # 전체 540, 4월 말까지 400
loancst = LoanCst(loan)

#### Assumption Sales ####
class Sales(Assumption_Base):
    def __init__(self):
        super().__init__()
        self._set_initial_data()
        
    def _set_initial_data(self):
        title, byname = "property", "자산매각"
        acc = self._set_account(title, byname)
        acc.salesamt = 109_000
        acc.addamt(idx.prjt[0], acc.salesamt)
        acc.subscd(idx.loan[-1], acc.salesamt)

        rnt = pd.DataFrame({
            'rntunt': [28_000, 28_000, 28_000, 28_000, 28_000],
            'mngunt': [2_000, 2_000, 2_000, 2_000, 2_000]},
            index=area.rentpy.index)
        rnt['area'] = area.rentpy
        rnt['rntamt'] = rnt['area'] * rnt['rntunt'] / untamt
        rnt['mngamt'] = rnt['area'] * rnt['mngunt'] / untamt
        rnt['dpstamt'] = rnt['rntamt'] * 6
        rnt['ttlamt'] = rnt['rntamt'] + rnt['mngamt']
        rnt['rntamty'] = rnt['rntamt'] * 12
        rnt['mngamty'] = rnt['mngamt'] * 12
        rnt['ttlamty'] = rnt['ttlamt'] * 12
        self.rnt = rnt

        _sumrow = rnt.sum(axis=0)
        _sumrow['rntunt'] = '-'
        _sumrow['mngunt'] = '-'
        _sumrow = DataFrame([_sumrow], index=['sum'], columns=rnt.columns)
        rntprt = pd.concat([rnt, _sumrow])
        _col = ['임대료', '관리비', '면적', '월임대료', '월관리비', '보증금', '월임관리비', '연임대료', '연관리비', '연임관리비']
        _idx = ['B1F', '1F', '2F', '3F', '4F', '합계']
        rntprt = DataFrame(rntprt.values, index=_idx, columns=_col)
        self.rntprt = rntprt

        vltn = {}
        vltn['rntamt'] = rnt['ttlamty'].sum()
        vltn['dpstamt'] = rnt['dpstamt'].sum()
        vltn['mngcst'] = 700
        # PM수수료 :   120원/평,월,  1,440원/평,연 <= 총괄 관리 및 관리 보고서 제출(비상근)
        # FM수수료 : 1,700원/평,월, 20,400원/평,연 <= 실제 시설관리(상근)
        # R&M    :   100원/평,월,  1,200원/평,연 <= 수선비, 장기수선충당금
        # 보험료   : 2,200원/평,월, 26,400원/평,연
        vltn['vcncy'] = 0.0
        vltn['NOI'] = (vltn['rntamt'] * (1 - vltn['vcncy'])) - vltn['mngcst']
        vltn['cap'] = 0.045
        vltn['valuation'] = vltn['NOI'] / vltn['cap'] + vltn['dpstamt']
        self.vltn = vltn
sales = Sales()

#### Assumption Costs ####
class Cost(Assumption_Base):
    def __init__(self, sales):
        super().__init__()
        self.sales = sales
        self.names = []
        self.key_main = []
        self._set_initial_data()

    def _set_initial_data(self):
        ## 토지비
        sgmnt           = Name("lnd", "토지비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "lndprchs", "토지매입비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_ttl     = 14_704#백만원
        acc.area        = area.lndpy
        acc.note        = f"{acc.area:,.0f}평 x {acc.amt_ttl * 1000 / acc.area:,.0f}천원/평"
        acc.addscd(idx.loan[0], acc.amt_ttl)

        title, byname   = "aqstntx", "취등록세"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0],     726)

        title, byname   = "jdclscvn", "법무사"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0],      12)

        title, byname   = "brkrg", "중개수수료"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0],     100)

        ## 도급공사비
        sgmnt           = Name("cstrn", "도급공사비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "drtcstrn", "도급공사비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_ttl     = 62_000  # 전층 상온 공사비
        acc.amt_prd     = 55_800
        acc.amt_rsrv    = 6_200
        acc.rate_rsrv   = 0.10

        # acc.amt_ttl    = 66_400 # 저온 1개층, 715억원 대비 공사비 140만원 할인 기준 667억원
        # acc.amt_prd    = 56_440
        # acc.amt_rsrv   =  9_960
        # acc.rate_rsrv  =   0.15

        # acc.amt_ttl    = 66_400 # 저온 1개층, 715억원 대비 공사비 140만원 할인 기준 667억원
        # acc.amt_prd    = 53_120
        # acc.amt_rsrv   = 13_280
        # acc.rate_rsrv  =   0.20

        acc.area_ttl    = area.ttlfloor
        acc.amt_unt     = acc.amt_ttl / acc.area_ttl
        acc.prcrate     = read_standard_process_rate_table(len(idx.cstrn), tolist=True)
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note        = f"{acc.area_ttl:,.0f}평 x {acc.amt_unt * 1000:,.0f}천원/평"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
        )
        acc.addscd(idx.loan[-1], acc.amt_rsrv)

        ## 간접공사비
        sgmnt           = Name("adcstrn", "간접공사비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "rmvlcst", "철거비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 1_215)

        title, byname   = "rmvlspvsn", "철거감리비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 60)

        title, byname   = "wtrelec", "인입비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_unt     = 0.060  # 백만원
        acc.amt_ttl     = area.ttlfloor * acc.amt_unt
        acc.note        = f"{area.ttlfloor:,.0f}평 x {acc.amt_unt * 1000:,.0f}천원/평"
        acc.addscd(idx.loan[0], acc.amt_ttl)

        title, byname   = "dsncst", "설계비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_unt     = 0.0706  # 백만원
        acc.amt_ttl     = area.ttlfloor * acc.amt_unt
        acc.note        = f"{area.ttlfloor:,.0f}평 x {acc.amt_unt * 1000:,.0f}천원/평"
        acc.addscd(idx.loan[0], acc.amt_ttl)

        title, byname   = "spvsncst", "감리비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_unt     = 0.082  # 백만원
        acc.amt_ttl     = area.ttlfloor * acc.amt_unt
        acc.note        = f"{area.ttlfloor:,.0f}평 x {acc.amt_unt * 1000:,.0f}천원/평"
        acc.addscd(idx.loan[0], acc.amt_ttl)

        ## 인허가비용 및 분부담금
        sgmnt           = Name("consent", "인허가 및 분부담금")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "cnsntcst", "인허가비용"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 528)

        title, byname   = "treecst", "대체산림자원조성비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 48)

        title, byname   = "farmland", "농지전용부담금"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 28)

        title, byname   = "wtrswg", "상하수도원인자부담금"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_unt     = 0.010  # 백만원
        acc.amt_ttl     = area.ttlfloor * acc.amt_unt
        acc.note        = f"{area.ttlfloor:,.0f}평 x {acc.amt_unt * 1000:,.0f}천원/평"
        acc.addscd(idx.loan[0], acc.amt_ttl)

        ## 판매비용
        sgmnt           = Name("slscst", "판매비용")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "rntbrkrg", "임대대행수수료"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.rnt_unt     = self.sales.rnt.rntamt.sum()
        acc.rnt_brcg_prd = 2  # 2months
        acc.rnt_brcg_fee = acc.rnt_unt * acc.rnt_brcg_prd
        acc.note        = f"월 임대료 {acc.rnt_unt:,.0f} x {acc.rnt_brcg_prd}개월"
        acc.addscd(idx.cstrn[-1], acc.rnt_brcg_fee / 2)  # 1_036)
        acc.addscd(idx.loan[-1], acc.rnt_brcg_fee / 2)

        title, byname   = "mrktgcst", "광고홍보비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_ttl     = 500
        acc.amt_unt     = acc.amt_ttl / 4
        acc.note        = "총 5억원을 4회 분할 지급 가정"
        acc.addscd(idx.loan[5], acc.amt_unt)  #
        acc.addscd(idx.loan[10], acc.amt_unt)
        acc.addscd(idx.loan[15], acc.amt_unt)
        acc.addscd(idx.loan[20], acc.amt_unt)

        ## 기타운영비
        sgmnt           = Name("oprtgcst", "기타운영비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "oprtgcpn", "시행사운영비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_unt     = 30
        acc.amt_ttl     = len(idx.cstrn) * acc.amt_unt
        acc.note        = f"{acc.amt_unt * 1000:,.0f}천원/월, {len(idx.cstrn)}개월"
        acc.addscd(idx.cstrn, [acc.amt_unt] * len(idx.cstrn))

        title, byname   = "trustfee", "관리신탁수수료"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 1_000)

        title, byname   = "dptybnk", "대리금융기관수수료"  # deputy banking fee
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.amt_unt     = 30
        acc.amt_ttl     = acc.amt_unt * 2
        acc.note        = f"{acc.amt_unt * 1000:,.0f}천원, 2년"
        acc.addscd(idx.loan[0], acc.amt_unt)
        acc.addscd(idx.loan[12], acc.amt_unt)

        title, byname   = "lawncstg", "법무/약정/사평/감평"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 190)

        # 재산세 : 과세기준일(6월 1일) 소유자, 9월 납부
        # 과세표준 : 공시지가 x 면적 x 70% (토지인 경우)
        # 세율 : 280만원 + 10억원 초과금액의 0.4% (별도합산대상의 경우)
        title, byname   = "prptytx", "재산세"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.aprsdvalue  = land.ttl_value / 1_000_000 # 공시지가
        acc.txbaseamt   = acc.aprsdvalue * 0.7 # 과세표준
        acc.txamt       = 2.8 + (acc.txbaseamt - 1_000) * 0.004 # 세율 적용
        acc.note        = f"공시지가({acc.aprsdvalue:,.0f}) x 70% x 약 0.4%(별도합산대상)"
        acc.dtlst       = [dt for dt in idx.loan if dt.month == 6]
        acc.addscd(acc.dtlst, [acc.txamt] * len(acc.dtlst))

        # 종합부동산세 : 과세기준일(6월 1일) 소유자
        # 과세표준 : 공시지가 x 면적 x 100%
        # 공제금액 : 80억원
        # 세율 : 200억원 이하 0.5%
        title, byname = "ttllndtx", "종부세"
        acc = self._set_account(title, byname, sgmnt.title)
        acc.aprsdvalue = land.ttl_value / 1_000_000  # 공시지가
        acc.txbaseamt = max((acc.aprsdvalue - 8_000) * 1.0, 0)  # 과세표준
        acc.txamt = acc.txbaseamt * 0.005  # 세율 적용
        acc.note = f"(공시지가({acc.aprsdvalue:,.0f}) - 8_000) x 0.5%(별도합산대상)"
        acc.dtlst = [dt for dt in idx.loan if dt.month == 6]
        acc.addscd(acc.dtlst, [acc.txamt] * len(acc.dtlst))

        title, byname   = "pmfee", "PM수수료"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "일식"
        acc.addscd(idx.loan[0], 200)

        title, byname   = "rgstrtnfee", "보존등기비"
        acc             = self._set_account(title, byname, sgmnt.title)
        acc.note        = "직간접공사비 등 x 약 3.4%"
        # 취득세 2.8%, 농특세 0.2%, 교육세 0.16%, 법무사 0.24%
        acc.addscd(idx.loan[-1], 2_456)

        title, byname   = "rsrvfnd", "예비비"
        acc = self._set_account(title, byname, sgmnt.title)
        acc.addscd(idx.loan[-1], 1_000)
cost = Cost(sales)

#### Assumption Accounts ####
class Acc(Assumption_Base):
    def __init__(self):
        super().__init__()

        title, byname = "oprtg", "운영계좌"
        acc = self._set_account(title, byname)

        title, byname = "repay", "상환계좌"
        acc = self._set_account(title, byname)
acc = Acc()









