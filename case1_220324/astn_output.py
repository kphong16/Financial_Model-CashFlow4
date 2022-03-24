#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import xlsxwriter
from datetime import date
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
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        
        wd('Index', wb.bold)
        _idx = self.astn.idx
        wd(['prjt', _idx.prd_prjt, _idx.prjt[0], _idx.prjt[-1]], fmt3)
        wd(['loan', _idx.mtrt, _idx.loan[0], _idx.loan[-1]], fmt3)
        wd(['cstrn', _idx.prd_cstrn, _idx.cstrn[0], _idx.cstrn[-1]], fmt3)
        wd.nextcell(1)
        
        wd('Equity', wb.bold)
        vallst = [
            ('title'        ,fmt1),
            ('amt_ntnl'     ,fmt1),
            ('amt_intl'     ,fmt1),
            ]
        for _val, _fmt in vallst:
            wd({_val: self.astn.equity.__dict__[_val]}, _fmt)
        wd.nextcell(1)
        
        wd('Loan', wb.bold)
        vallst = [
            ('title'        ,fmt1),
            ('rnk'          ,fmt1),
            ('amt_ntnl'     ,fmt1),
            ('amt_intl'     ,fmt1),
            ('rate_fee'     ,fmt2),
            ('rate_IR'      ,fmt2),
            ('rate_fob'     ,fmt2),
            ('allin'        ,fmt2),
            ]
        for _val, _fmt in vallst:
            tmplst = [getattr(item, _val) for item in loan.dct.values()]
            wd({_val: tmplst}, _fmt)
        wd.nextcell(1)
        
        wd(['Maturity', self.astn.loan.mtrt], fmt1)
        wd(['ttl_ntnl', self.astn.loan.ttl_ntnl], fmt1)
        wd(['rate_arng', self.astn.loan.rate_arng], fmt2)
        wd(['allin_ttl', self.astn.loan.allin_ttl()], fmt2)
        

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
        
        ## Write loan astn
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        
        wd('Area(m2)', wb.bold)
        wd(area.mtrx, fmt=wb.num, valdrtn='col')
        wd.nextcell(1)
        
        wd('Area(py)', wb.bold)
        wd(area.mtrxpy, fmt=wb.num, valdrtn='col')
        wd.nextcell(1)
        
        wd('Rent', wb.bold)
        wd(sales.sales.rnt, fmt=wb.num, valdrtn='col')
        wd.nextcell(1)
        
        wd('Valuation', wb.bold)
        vallst = [
            ('rntamt'       ,fmt1),
            ('dpstamt'      ,fmt1),
            ('mngcst'       ,fmt1),
            ('NOI'          ,fmt1),
            ('cap'          ,fmt2),
            ('valuation'    ,fmt1),
            ]
        for _val, _fmt in vallst:
            wd({_val: sales.sales.vltn[_val]}, _fmt)
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
        wd(idx, wb.date, 'col')
        
        wd.setcell(cell)
        wd.nextcell(1, drtn='col')
        
        ## Write operating account balance
        tmpfmt = [wb.bold, wb.bold, wb.num]
        tmpdct = {
            "운영_기초"     : wb.extnddct(
                {"기초잔액"     : oprtg.df.bal_strt},
                ),
            "CashIn"      : wb.extnddct(
                {"Equity"     : equity.ntnl.df.amt_out},
                {"Loan_"+key  : item.ntnl.df.amt_out for key, item in loan.dct.items()},
                {"Sales_"+key : item.df.amt_out for key, item in sales.dct.items()},
                ),
            "상환_loan"    : wb.extnddct(
                {"Loan_"+key  : item.ntnl.df.amt_in for key, item in loan.dct.items()},
                ),
            "운영_유입"     : wb.extnddct(
                {"현금유입"     : oprtg.df.amt_in},
                ),
            "조달비용"      : wb.extnddct(
                {"Loan_"+item.title: item.df.amt_in for key, item in loancst.dct.items()},
                ),
            "금융비용"      : wb.extnddct(
                {"Fee_"+key   : item.fee.df.amt_in for key, item in loan.dct.items()},
                {"IR_"+key   : item.IR.df.amt_in for key, item in loan.dct.items()},
                {"Fob_"+key   : item.fob.df.amt_in for key, item in loan.dct.items() if item.rate_fob > 0},
                ),
            }
        
        ## Write operating costs
        tmpdct = wb.extnddct(
            tmpdct,
            {keysgmnt: {item.byname: item.df.amt_in for key, item in itemsgmnt.items()} 
                for keysgmnt, itemsgmnt in cost.dctsgmnt.items()}
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
                 
        ## Write dictionary
        wd(tmpdct, tmpfmt, valdrtn='col', drtn='row')
        
        
    #### Write Loan ####
    def _writeloan(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("financing")
        wd = WriteWS(ws, Cell(0,0))
        
        # Write Head
        ws.set_column("A:A", 12)
        wd("ASSUMPTION", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.file_adrs)
        cell = wd.nextcell(2)
        
        # Write Index
        wd.nextcell(3)
        wd(idx, wb.date, 'col')
        wd.setcell(cell)
        wd.nextcell(1, drtn='col')
        
        tmpfmt = [wb.bold, wb.bold, wb.bold, wb.num]
        tmpdct = {}
        # Write Loan
        for rnk in loan.rnk():
            tmpdct["Loan_"+loan.by_rnk(rnk).title] = wb.dct_loan(loan.by_rnk(rnk))
        # Write Equity
        tmpdct["Equity_"+equity.title] = wb.dct_loan(equity)
        
        # Write Dictionary
        wd(tmpdct, tmpfmt, valdrtn='col', drtn='row')
        #wb.write_dct_col("financing", row, col, tmpdct, tmpfmt)
        
        
    #### Write Financial Balance Table ####
    def _writefbal(self):
        global idx, oprtg, equity, loan, loancst, sales, cost, area
        
        # new worksheet
        wb = self.wb
        ws = wb.add_ws("financial_balance")
        wd = WriteWS(ws, Cell(0,0))
                
        ## Write head
        ws.set_column("A:A", 12)
        ws.set_column("B:B", 18)
        wd("Financial Balance Table", wb.bold)
        wd("Written at:" + wb.now)
        wd(self.file_adrs)
        cell = wd.nextcell(2)
        
        ## Write financial balance table
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        fmt4 = [wb.bold, wb.nml, wb.num]
        
        wd('Sales', wb.bold)
        ttl_sales = 0
        for key, item in sales.dct.items():
            wd([key, "", item.salesamt], fmt4)
            ttl_sales += item.salesamt
        wd(["Total amt", "", ttl_sales], fmt4)
        wd.nextcell(2)
        
        wd('Costs', wb.bold)
        ttl_costs = 0
        
        # Write operating costs
        for keym in cost.key_main:
            wd(keym, wb.bold, drtn='col')
        
            sum_balend = 0
            for key, item in cost.dctsgmnt[keym].items():
                if 'note' in item.__dict__.keys():
                    wd([item.byname, item.bal_end[-1], item.note], [wb.nml, wb.num, wb.nml])
                else:
                    wd([item.byname, item.bal_end[-1]], [wb.nml, wb.num])
                sum_balend += item.bal_end[-1]
            ttl_costs += sum_balend
            wd(["subtotal", sum_balend], [wb.bold, wb.num])
            wd.nextcell(-1, 'col')
            
        # Write financing costs
        for rnk in loan.rnk():
            ln = loan.by_rnk(rnk)
            wd(ln.title, wb.bold, drtn='col')
            
            sum_balend = 0
            if ln.rate_fee > 0:
                wd(["fee", ln.fee.bal_end[-1]], [wb.nml, wb.num])
                sum_balend += ln.fee.bal_end[-1]
            if ln.rate_IR > 0:
                wd(["IR", ln.IR.bal_end[-1]], [wb.nml, wb.num])
                sum_balend += ln.IR.bal_end[-1]
            if ln.rate_fob > 0:
                wd(["fob", ln.fob.bal_end[-1]], [wb.nml, wb.num])
                sum_balend += ln.fob.bal_end[-1]
            ttl_costs += sum_balend
            wd(["subtotal", sum_balend], [wb.bold, wb.num])
            wd.nextcell(-1, 'col')
            
        for key, item in loancst.dct.items():
            wd(key, wb.bold, drtn='col')
            
            wd([item.byname, item.bal_end[-1]], [wb.nml, wb.num])
            ttl_costs += item.bal_end[-1]
            wd.nextcell(-1, 'col')
            
        wd(["Total", "", ttl_costs], [wb.bold, wb.nml, wb.num])
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        