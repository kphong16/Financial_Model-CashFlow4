#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-03-08

@author: KP_Hong
"""

import xlsxwriter
from datetime import date
from cafle import Write

        
class WriteCF:
    def __init__(self, file_adrs, data):
        self.file_adrs  = file_adrs
        self.data       = data
        self.wb         = Write(file_adrs)
        
        self._writecf()
        self._writeloan()
        #self._writecst()
        
        self.wb.close()
        
    #### Write Cashflow ####
    def _writecf(self):
        # new worksheet
        wb = self.wb
        ws = wb.add_ws("cashflow")
        
        # set variables
        idx     = self.data.idx.prjt
        oprtg   = self.data.acc.oprtg
        equity  = self.data.equity.equity
        loan    = self.data.loan.loan
        loancst = self.data.loancst
        sales   = self.data.sales.sales
        cost    = self.data.cost
        
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
            
            #{"Cost" : {key: item.df.amt_in for key, item in cost.dct.items()}}
            #{key: {key2: item2.df.amt_in for key2, item2 in item.dct.items()}
            #for key, item in cost.dct.items()}
            )
        tmpdct = wb.extnddct(
            tmpdct, {
            "상환_equity" : 
                {"Equity" : equity.ntnl.df.amt_in},
            "운영_유출"    : 
                {"현금유출" : oprtg.df.amt_out},
            "운영_기말"    : 
                {"기말잔액" : oprtg.df.bal_end},
             }
             )
                 
        ## Write dictionary
        wb.write_dct_col("cashflow", row, col, tmpdct, tmpfmt)
        
        
    #### Write Loan ####
    def _writeloan(self):
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("financing")
        
        # Setting Variables
        idx = self.data.idx.prjt
        oprtg = self.data.acc.oprtg
        equity = self.data.equity.equity
        loan = self.data.loan.loan
        loancst = self.data.loancst
        sales = self.data.sales.sales
        cost = self.data.cost
        
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
        for rnk in loan.rnk:
            tmpdct["Loan_"+loan[rnk].title] = wb.dct_loan(loan[rnk])
        # Write Equity
        tmpdct["Equity_"+equity.title] = wb.dct_loan(equity)
        
        # Write Dictionary
        wb.write_dct_col("financing", row, col, tmpdct, tmpfmt)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        