#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 17:41:35 2021

@author: KP_Hong
"""

import xlsxwriter

# Get Attributes from Main
idx = None
equity = None
loan = None
sales = None
fnccst = None
cost = None
acc = None

class WriteCF(object):
    def __init__(self, file_adrs):
        self.file_adrs = file_adrs
        self.wb = xlsxwriter.Workbook(self.file_adrs)
        self.ws = self.wb.add_worksheet("cashflow")
        
        self.fmt_bold = self.wb.add_format({'bold': True})
        self.fmt_date = self.wb.add_format({'num_format': 'yyyy-mm-dd'})
        self.fmt_num1 = self.wb.add_format({'num_format': '#,##0'})
        self.fmt_num2 = self.wb.add_format({'num_format': '#,##0.0'})
        self.fmt_pct = self.wb.add_format({'num_format': '0.0%'})
        
        self.col = 0
        self.row = 3
        
        self._writecf()
        
        self.wb.close()
    
    def _writecf(self):
        # Write Index
        self.ws.write_column(self.row+2, self.col, idx.index, self.fmt_date)
        self.col += 1
        
        # Write OprtgAcc Balance
        self.ws.write_string(self.row, self.col, "운영계좌", self.fmt_bold)
        self.ws.write_string(self.row + 1, self.col, "기초잔액", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, acc.oprtg.df.bal_strt, self.fmt_num1)
        self.col += 1
        
        # Write CashIn
        self.ws.write_string(self.row, self.col, "CashIn", self.fmt_bold)
        self.ws.write_string(self.row + 1, self.col, "Equity", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, equity.ntnl.df.amt_sub, self.fmt_num1)
        self.col += 1
        
        self.ws.write_string(self.row + 1, self.col, "LoanTrA", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, loan.tra.ntnl.df.amt_sub, self.fmt_num1)
        self.col += 1
        
        self.ws.write_string(self.row + 1, self.col, "LoanTrB", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, loan.trb.ntnl.df.amt_sub, self.fmt_num1)
        self.col += 1
        
        self.ws.write_string(self.row + 1, self.col, "Sales", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, sales.df.amt_sub, self.fmt_num1)
        self.col += 1
        
        # Write OprtgAcc Amount_add
        self.ws.write_string(self.row, self.col, "운영계좌", self.fmt_bold)
        self.ws.write_string(self.row + 1, self.col, "현금유입", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, acc.oprtg.df.amt_add, self.fmt_num1)
        self.col += 1
        
        # Write CashOut
        self.ws.write_string(self.row, self.col, "FncCost", self.fmt_bold)
        cstlst = fnccst.lfkey("account", return_val="dict")
        for dct in cstlst:
            self.ws.write_string(self.row + 1, self.col, dct["byname"], self.fmt_bold)
            self.ws.write_column(self.row + 2, self.col, dct["account"].df.amt_add.values, self.fmt_num1)
            self.col += 1
            
        self.ws.write_string(self.row, self.col, "IRnFee", self.fmt_bold)
        
        self.ws.write_string(self.row + 1, self.col, "TrA_fee", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, loan.tra.fee.df.amt_add, self.fmt_num1)
        self.col += 1
        
        self.ws.write_string(self.row + 1, self.col, "TrB_fee", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, loan.trb.fee.df.amt_add, self.fmt_num1)
        self.col += 1
        
        self.ws.write_string(self.row + 1, self.col, "TrA_IR", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, loan.tra.IR.df.amt_add, self.fmt_num1)
        self.col += 1
        
        self.ws.write_string(self.row + 1, self.col, "TrB_IR", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, loan.trb.IR.df.amt_add, self.fmt_num1)
        self.col += 1

        for key, item in cost._dct.items():
            cstlst = cost.lfkey("account", return_val="dict", dct_ipt=item)
            for dct in cstlst:
                self.ws.write_string(self.row, self.col, key, self.fmt_bold)
                self.ws.write_string(self.row + 1, self.col, dct["byname"], self.fmt_bold)
                self.ws.write_column(self.row + 2, self.col, dct["account"].df.amt_add.values, self.fmt_num1)
                self.col += 1
        
        # Write OprtgAcc Amount_sub
        self.ws.write_string(self.row, self.col, "운영계좌", self.fmt_bold)
        self.ws.write_string(self.row + 1, self.col, "현금유출", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, acc.oprtg.df.amt_sub, self.fmt_num1)
        self.col += 1
        
        # Write OprtgAcc Balance_end
        self.ws.write_string(self.row, self.col, "운영계좌", self.fmt_bold)
        self.ws.write_string(self.row + 1, self.col, "기말잔액", self.fmt_bold)
        self.ws.write_column(self.row + 2, self.col, acc.oprtg.df.bal_end, self.fmt_num1)
        self.col += 1