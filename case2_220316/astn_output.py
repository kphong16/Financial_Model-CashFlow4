#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import xlsxwriter
from datetime import date
from cafle import Write, WriteWS

        
class WriteCF:
    def __init__(self, file_adrs, astn):
        self.file_adrs  = file_adrs
        self.astn       = astn
        self.wb         = Write(file_adrs)
        
        self._writeastn()
        self._writecf()
        self._writeloan()
        self._writefbal()
        
        self.wb.close()
        
    #### Write Cashflow ####
    def _writecf(self):
        # new worksheet
        wb = self.wb
        ws = wb.add_ws("cashflow")
        
        # set variables
        idx     = self.astn.idx.prjt
        oprtg   = self.astn.acc.oprtg
        equity  = self.astn.equity
        loan    = self.astn.loan
        loancst = self.astn.loancst
        sales   = self.astn.sales.sales
        cost    = self.astn.cost
        
        ## Write head
        ws.set_column(0, 0, 12)
        ws.write(0, 0, "CASH FLOW", wb.bold)
        ws.write(1, 0, "Written at: " + wb.now)
        ws.write(2, 0, self.file_adrs)
        
        row = 5
        col = 0
        
        ## Write index
        ws.write_column(row+2, col, idx, wb.date)
        col += 1
        
        ## Write operating account balance
        tmpfmt = [wb.bold, wb.bold, wb.num]
        tmpdct = {
            "운영_기초"     : wb.extnddct(
                {"기초잔액"     : oprtg.df.bal_strt},
                ),
            "CashIn"      : wb.extnddct(
                {"Equity"     : equity.ntnl.df.amt_out},
                {"Loan_"+key  : item.ntnl.df.amt_out for key, item in loan.dct.items()},
                {"Sales"      : sales.df.amt_out},
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
        wb.write_dct_col("cashflow", row, col, tmpdct, tmpfmt)
        
        
    #### Write Loan ####
    def _writeloan(self):
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("financing")
        
        # Setting Variables
        idx = self.astn.idx.prjt
        oprtg = self.astn.acc.oprtg
        equity = self.astn.equity
        loan = self.astn.loan
        loancst = self.astn.loancst
        sales = self.astn.sales.sales
        cost = self.astn.cost
        
        # Write Head
        ws.set_column(0, 0, 12)
        ws.write(0, 0, "FINANCING", wb.bold)
        ws.write(1, 0, "Written at: " + wb.now)
        ws.write(2, 0, self.file_adrs)
        
        row = 5
        col = 0
        
        # Write Index
        ws.write_column(row+3, col, idx, wb.date)
        col += 1    
        
        
        tmpfmt = [wb.bold, wb.bold, wb.bold, wb.num]
        tmpdct = {}
        # Write Loan
        for rnk in loan.rnk():
            tmpdct["Loan_"+loan.by_rnk(rnk).title] = wb.dct_loan(loan.by_rnk(rnk))
        # Write Equity
        tmpdct["Equity_"+equity.title] = wb.dct_loan(equity)
        
        # Write Dictionary
        wb.write_dct_col("financing", row, col, tmpdct, tmpfmt)

        
    #### Write Astn ####
    def _writeastn(self):
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("assumption")
        
        # Setting Variables
        idx = self.astn.idx.prjt
        oprtg = self.astn.acc.oprtg
        equity = self.astn.equity
        loan = self.astn.loan
        loancst = self.astn.loancst
        sales = self.astn.sales.sales
        cost = self.astn.cost
        
        # Write Head
        ws.set_column(0, 0, 12)
        ws.write(0, 0, "ASSUMPTION", wb.bold)
        ws.write(1, 0, "Written at: " + wb.now)
        ws.write(2, 0, self.file_adrs)
        
        row = 5
        col = 0
        
        ## Write loan astn
        wd = WriteWS(ws, row, col)
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        
        wd('Index', wb.bold)
        _idx = self.astn.idx
        wd(['prjt', _idx.prd_prjt, _idx.prjt[0], _idx.prjt[-1]], fmt3)
        wd(['loan', _idx.mtrt, _idx.loan[0], _idx.loan[-1]], fmt3)
        wd(['cstrn', _idx.prd_cstrn, _idx.cstrn[0], _idx.cstrn[-1]], fmt3)
        wd.row += 1
        
        wd('Equity', wb.bold)
        vallst = [
            ('title'        ,fmt1),
            ('amt_ntnl'     ,fmt1),
            ('amt_intl'     ,fmt1),
            ]
        for _val, _fmt in vallst:
            wd({_val: self.astn.equity.__dict__[_val]}, _fmt, drtn='col')
        wd.row += 3
        wd.col = 0
        
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
            wd({_val: tmplst}, _fmt, drtn='col')
        wd.row += 3
        wd.col = 0
        wd(['Maturity', self.astn.loan.mtrt], fmt1)
        wd(['ttl_ntnl', self.astn.loan.ttl_ntnl], fmt1)
        wd(['rate_arng', self.astn.loan.rate_arng], fmt2)
        wd(['allin_ttl', self.astn.loan.allin_ttl()], fmt2)
        
        
    #### Write Financial Balance Table ####
    def _writefbal(self):
        # new worksheet
        wb = self.wb
        ws = wb.add_ws("financial_balance")
        
        # set variables
        idx     = self.astn.idx.prjt
        oprtg   = self.astn.acc.oprtg
        equity  = self.astn.equity
        loan    = self.astn.loan
        loancst = self.astn.loancst
        sales   = self.astn.sales
        cost    = self.astn.cost
        
        ## Write head
        ws.set_column(0, 0, 12)
        ws.write(0, 0, "Financial Balance Table", wb.bold)
        ws.write(1, 0, "Written at: " + wb.now)
        ws.write(2, 0, self.file_adrs)        

        row = 5
        col = 0
        
        ## Write financial balance table
        wd = WriteWS(ws, row, col)
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        fmt4 = [wb.bold, wb.nml, wb.num]
        
        wd('Sales', wb.bold)
        ttl_sales = 0
        for key, item in sales.dct.items():
            wd([key, "", item.salesamt], fmt4)
            ttl_sales += item.salesamt
        wd(["Total amt", "", ttl_sales], fmt4, cellno=2)
        
        wd('Costs', wb.bold)
        ttl_costs = 0
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        