#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import xlsxwriter
from datetime import date
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from cafle import Write, WriteWS, Cell

        
class WriteCF:
    idx = None
    oprtg = None
    equity = None
    loan = None
    loancst = None
    sales = None
    cost = None
    area = None
    
    def __init__(self, file_adrs, astn):
        self.file_adrs  = file_adrs
        self.astn       = astn
        self.wb         = Write(file_adrs)

        # Setting Variables
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        idx = self.astn.idx.prjt
        oprtg = self.astn.acc.oprtg
        equity = self.astn.equity
        loan = self.astn.loan
        loancst = self.astn.loancst
        sales = self.astn.sales
        cost = self.astn.cost
        area = self.astn.area
        
        self._writeastn()
        self._writevltn()
        self._writecf()
        self._writeloan()
        self._writefbal()
        self._writecstrn()
        
        self.wb.close()

    #### Write Astn ####
    def _writeastn(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("assumption")
        wd = WriteWS(ws, Cell(0,0))
        
        # Write Head
        ws.set_column("A:K", 12)
        wd("ASSUMPTION", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.file_adrs)
        wd.nextcell(2)

        ## Write loan astn
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        
        wd('[Index]', wb.bold)
        _idx = self.astn.idx
        fmt = [wb.bold, wb.month, wb.date, wb.date]
        wd(['사업기간', _idx.prd_prjt, _idx.prjt[0], _idx.prjt[-1]], fmt)
        wd(['대출기간', _idx.mtrt, _idx.loan[0], _idx.loan[-1]], fmt)
        wd(['건설기간', _idx.prd_cstrn, _idx.cstrn[0], _idx.cstrn[-1]], fmt)
        wd.nextcell(1)
        
        wd('[Sales: Rent]', wb.bold)
        wd(sales.rntprt, fmt=wb.num, valdrtn='col')
        wd.nextcell(1)
        
        wd('[Valuation]', wb.bold)
        wd(['연임관리비', sales.vltn['rntamt']], fmt1)
        wd(['운영비용',  sales.vltn['mngcst']], fmt1)
        wd(['NOI',     sales.vltn['NOI']], fmt1)
        wd(['Cap.rate', sales.vltn['cap']], fmt2)
        wd(['보증금',    sales.vltn['dpstamt']], fmt1)
        wd(['Valuation', sales.vltn['valuation']], fmt1)
        wd.nextcell(1)
        
        wd('[Cost: 도급공사비]', wb.bold)
        wd(['총 공사비', cost.drtcstrn.amt_ttl], [wb.bold, wb.num])
        wd(['단위공사비', cost.drtcstrn.amt_unt*1_000, cost.drtcstrn.area_ttl], [wb.bold, wb.num, wb.num])
        wd(['기성공사비', cost.drtcstrn.amt_prd], [wb.bold, wb.num])
        wd(['유보공사비', cost.drtcstrn.amt_rsrv, cost.drtcstrn.rate_rsrv], [wb.bold, wb.num, wb.pct])
        wd.nextcell(1)
        
        wd('[Equity]', wb.bold)
        vallst = [
            ('title'        ,'구분'        ,fmt1),
            ('amt_ntnl'     ,'대출금액'     ,fmt1),
            ('amt_intl'     ,'최초인출'     ,fmt1),
            ]
        for _key, _byname, _fmt in vallst:
            tmplst = [getattr(_eqt, _key) for _eqt in equity.dct.values()]
            wd({_byname: tmplst}, _fmt)
        wd.nextcell(1)
        
        wd('[Loan]', wb.bold)
        vallst = [
            ('title'        ,'구분'       ,fmt1),
            ('rnk'          ,'순위'       ,fmt1),
            ('amt_ntnl'     ,'대출금액'    ,fmt1),
            ('amt_intl'     ,'최초인출'    ,fmt1),
            ('rate_fee'     ,'수수료율'    ,fmt2),
            ('rate_IR'      ,'금리'       ,fmt2),
            ('rate_fob'     ,'미인출수수료' ,fmt2),
            ('allin'        ,'All_in'    ,fmt2),
            ]
        for _key, _byname, _fmt in vallst:
            tmplst = [getattr(_loan, _key) for _loan in loan.dct.values()]
            wd({_byname: tmplst}, _fmt)
        wd.nextcell(1)
        
        wd(['만기'       , _idx.mtrt], [wb.bold, wb.month])
        wd(['총 대출금액'  , self.astn.loan.ttl_ntnl], fmt1)
        wd(['주관수수료'   , self.astn.loan.rate_arng], fmt2)
        wd(['총괄 All_in', self.astn.loan.allin_ttl()], fmt2)

    #### Write Valuation ####
    def _writevltn(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("valuation")
        wd = WriteWS(ws, Cell(0,0))
        
        # Write Head
        ws.set_column("A:K", 12)
        wd("VALUATION", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.file_adrs)
        wd.nextcell(2)
        
        ## Write valuation astn
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        
        wd('면적표(m2)', wb.bold)
        wd(area.mtrx, fmt=wb.num, valdrtn='col')
        wd.nextcell(1)
        
        wd('면적표(py)', wb.bold)
        wd(area.mtrxpy, fmt=wb.num, valdrtn='col')
        wd.nextcell(1)
        
        wd('임대수익표', wb.bold)
        wd(sales.rntprt, fmt=wb.num, valdrtn='col')
        wd.nextcell(1)
        
        wd('Valuation', wb.bold)
        _vltn = sales.vltn
        wd(['연임관리비', _vltn['rntamt'], ""], [wb.bold, wb.num, wb.nml])
        wd(['운영비용', _vltn['mngcst'], ""], [wb.bold, wb.num, wb.nml])
        #wd(['공실률', _vltn['vcncy'], ""], [wb.bold, wb.pct, wb.nml])
        wd(['NOI', _vltn['NOI'], "임관리수익 - 운영비용"], [wb.bold, wb.num, wb.nml])
        wd(['Cap.rate', _vltn['cap'], ""], [wb.bold, wb.pct, wb.nml])
        wd(['보증금', _vltn['dpstamt'], ""], [wb.bold, wb.num, wb.nml])
        wd(['Valuation', _vltn['valuation'], "NOI / cap + 보증금"], [wb.bold, wb.num, wb.nml])
        wd.nextcell(1)

    #### Write Cashflow ####
    def _writecf(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # new worksheet
        wb = self.wb
        ws = wb.add_ws("cashflow")
        wd = WriteWS(ws, Cell(0,0))
                
        ## Write head
        ws.set_column(0, 0, 12)
        wd("CASH FLOW", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.file_adrs)
        cell = wd.nextcell(2)
        
        ## Write index
        wd.nextcell(2)
        wd(idx, wb.date, valdrtn='col', drtn='row')
        wd("sum", wb.nml)
        
        wd.setcell(cell)
        wd.nextcell(1, drtn='col')
        
        ## Write operating account balance
        tmpfmt = [wb.bold, wb.bold, wb.num]
        tmpdct = {
            "운영_기초"     : wb.extnddct(
                {"기초잔액"     : oprtg.df.bal_strt},
                ),
            "현금유입"      : wb.extnddct(
                {"Equity"     : equity.ntnl.df.amt_out},
                {"Loan_"+key  : item.ntnl.df.amt_out for key, item in loan.dct.items()},
                {"매출_"+item.byname : item.df.amt_out for key, item in sales.dct.items()},
                ),
            "상환_loan"    : wb.extnddct(
                {"상환_"+key  : item.ntnl.df.amt_in for key, item in loan.dct.items()},
                ),
            "운영_유입"     : wb.extnddct(
                {"현금유입"     : oprtg.df.amt_in},
                ),
            "조달비용"      : wb.extnddct(
                {item.byname : item.df.amt_in for key, item in loancst.dct.items()},
                ),
            "금융비용"      : wb.extnddct(
                {"Fee_"+key   : item.fee.df.amt_in for key, item in loan.dct.items()},
                {"IR_"+key   : item.IR.df.amt_in for key, item in loan.dct.items()},
                {"미인출_"+key   : item.fob.df.amt_in for key, item in loan.dct.items() if item.rate_fob > 0},
                ),
            }
        
        ## Write operating costs
        tmpdct = wb.extnddct(
            tmpdct,
            {name.byname: {item.byname: item.df.amt_in for key, item in cost.dctsgmnt[name.title].items()}
                for name in cost.names}
            )
            
        tmpdct = wb.extnddct(
            tmpdct, {
            "상환_equity" : 
                {"Equity" : equity.ntnl.df.amt_in},
            "운영_유출"    : 
                {"현금유출" : oprtg.df.amt_out},
            "운영_기말"    : 
                {"기말잔액" : oprtg.df.bal_end},
            })

        ## Add sum
        dctsum = {}
        for key, dct in tmpdct.items():
            dctsum[key] = {}
            for key2, srs in dct.items():
                if key2 in ['기초잔액', '기말잔액']:
                    tmpval = "-"
                else:
                    tmpval = sum(srs)
                dctsum[key][key2] = pd.concat([srs, Series([tmpval], index=['합계'])])

        ## Write dictionary
        wd(dctsum, tmpfmt, valdrtn='col', drtn='row')

    #### Write Loan ####
    def _writeloan(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("financing")
        wd = WriteWS(ws, Cell(0,0))
        
        # Write Head
        ws.set_column("A:A", 12)
        wd("FINANCING", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.file_adrs)
        cell = wd.nextcell(2)
        
        # Write Index
        wd.nextcell(3)
        wd(idx, wb.date, valdrtn='col', drtn='row')
        wd("sum", wb.nml)

        wd.setcell(cell)
        wd.nextcell(1, drtn='col')
        
        tmpfmt = [wb.bold, wb.bold, wb.bold, wb.num]
        tmpdct = {}
        # Write Loan
        for rnk in loan.rnk:
            tmpdct["Loan_"+loan.by_rnk(rnk).title] = wb.dctprt_loan(loan.by_rnk(rnk))
        # Write Equity
        tmpdct["Equity_"+equity.title] = wb.dctprt_loan(equity)

        ## Add sum
        dctsum = {}
        for key, dct in tmpdct.items():
            dctsum[key] = {}
            for key2, dct2 in dct.items():
                dctsum[key][key2] = {}
                for key3, srs in dct2.items():
                    if key3 in ['대출잔액', '누적이자', '누적수수료', '누적미인출']:
                        tmpval = "-"
                    else:
                        tmpval = sum(srs)
                    dctsum[key][key2][key3] = pd.concat([srs, Series([tmpval], index=['sum'])])

        # Write Dictionary
        wd(dctsum, tmpfmt, valdrtn='col', drtn='row')
        #wb.write_dct_col("financing", row, col, tmpdct, tmpfmt)

    #### Write Financial Balance Table ####
    def _writefbal(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # new worksheet
        wb = self.wb
        ws = wb.add_ws("financial_balance")
        wd = WriteWS(ws, Cell(0,0))
        amt_lst = []
                
        ## Write head
        ws.set_column("A:A", 16)
        ws.set_column("B:B", 22)
        ws.set_column("C:D", 14)
        ws.set_column("E:E", 40)
        wd("Financial Balance Table", wb.bold)
        wd("Written at:" + wb.now)
        wd(self.file_adrs)
        cell = wd.nextcell(2)
        
        ## Write financial balance table
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        fmt4 = [wb.bold, wb.nml, wb.num]
        
        ## Sales
        wd('Sales', wb.bold)
        ttl_sales = 0
        for key, item in sales.dct.items():
            wd(["매출_"+item.byname, "", item.salesamt], fmt4)
            ttl_sales += item.salesamt
        wd(["Total", "", ttl_sales], fmt4)
        wd.nextcell(2)
        
        ## Costs
        wd('Costs', wb.bold)
        cell=wd(['구분1', '구분2', '금액', '비율', '비고'], wb.bold)
        ttl_costs = 0
        
        # Write operating costs
        for name in cost.names:
            wd(name.byname, wb.bold, drtn='col')
            keym = name.title

            sum_balend = 0
            for key, item in cost.dctsgmnt[keym].items():
                _val = item.bal_end[-1]
                if 'note' in item.__dict__.keys():
                    wd([item.byname, _val, "", item.note], [wb.nml, wb.num, wb.nml, wb.nml])
                else:
                    wd([item.byname, _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            ttl_costs += sum_balend
            wd(["subtotal", sum_balend], [wb.bold, wb.num])
            amt_lst.append(sum_balend)
            wd.nextcell(-1, 'col')
            
        # Write financing costs
        for rnk in loan.rnk:
            ln = loan.by_rnk(rnk)
            wd("대출_"+ln.title, wb.bold, drtn='col')
            
            sum_balend = 0
            if ln.rate_fee > 0:
                _val = ln.fee.bal_end[-1]
                wd(["fee", _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            if ln.rate_IR > 0:
                _val = ln.IR.bal_end[-1]
                wd(["IR", _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            if ln.rate_fob > 0:
                _val = ln.fob.bal_end[-1]
                wd(["미인출", _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            ttl_costs += sum_balend
            wd(["subtotal", sum_balend], [wb.bold, wb.num])
            amt_lst.append(sum_balend)
            wd.nextcell(-1, 'col')
            
        for key, item in loancst.dct.items():
            wd(item.byname, wb.bold, drtn='col')
            
            wd(["", item.bal_end[-1]], [wb.nml, wb.num])
            amt_lst.append(item.bal_end[-1])
            ttl_costs += item.bal_end[-1]
            wd.nextcell(-1, 'col')
            
        wd(["Total", "", ttl_costs], [wb.bold, wb.nml, wb.num])
        amt_lst.append(ttl_costs)
        
        # Write ratio
        wb.write_col(
            Cell(cell.row, cell.col+3), 
            [val/ttl_costs for val in amt_lst], 
            fmt=wb.pct, 
            wsname=ws)
        
        wd.setcell(Cell(cell.row + len(amt_lst), cell.col))
        wd.nextcell(2)    
        ## Profit
        wd('Profit', wb.bold)
        wd(['Equity', '', equity.amt_ntnl], [wb.bold, wb.num, wb.num])
        wd(['매출_자산매각', '', ttl_sales], [wb.bold, wb.num, wb.num])
        wd(['총 사업비', '', ttl_costs], [wb.bold, wb.num, wb.num])
        wd(['사업이익', '', equity.amt_ntnl + ttl_sales - ttl_costs], [wb.bold, wb.num, wb.numb])
        
    #### Write Construction ####
    def _writecstrn(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("construction")
        wd = WriteWS(ws, Cell(0,0))
        
        # Write Head
        ws.set_column("A:E", 13)
        wd("CONSTRUCTION", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.file_adrs)
        cell = wd.nextcell(2)
        
        # Write Note
        wd(['총 공사비', cost.drtcstrn.amt_ttl], [wb.bold, wb.num])
        wd(['기성공사비', cost.drtcstrn.amt_prd], [wb.bold, wb.num])
        wd(['유보공사비', cost.drtcstrn.amt_rsrv], [wb.bold, wb.num])
        wd(['유보비율', cost.drtcstrn.rate_rsrv], [wb.bold, wb.pct])
        wd(['총 면적', cost.drtcstrn.area_ttl], [wb.bold, wb.num])
        wd(['단위공사비', cost.drtcstrn.amt_unt*1_000], [wb.bold, wb.num])
        wd(['비고', cost.drtcstrn.note], [wb.bold, wb.nml])
        
        # Write index and data
        wd.nextcell(2)
        wd(['Index', '공정률', '누적공정률', '공사비', '누적공사비'], wb.bold)
        wd(self.astn.idx.cstrn, wb.date, 'col', 'col')
        wd(cost.drtcstrn.prcrate, wb.pct, 'col', 'col')
        wd(cost.drtcstrn.prcrate_cml, wb.pct, 'col', 'col')
        
        _amt = [cost.drtcstrn.amt_prd * val for val in cost.drtcstrn.prcrate]
        _amt[-1] = _amt[-1] + cost.drtcstrn.amt_rsrv
        wd(_amt, wb.num, 'col', 'col')
        
        _amt_cml = np.cumsum(_amt).tolist()        
        cell = wd(_amt_cml, wb.num, 'col', 'row')
        wd.setcell(cell.row, 0)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        