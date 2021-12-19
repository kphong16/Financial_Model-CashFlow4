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
        
        self.fmt_bold = self.wb.add_format({'bold': True})
        self.fmt_date = self.wb.add_format({'num_format': 'yyyy-mm-dd'})
        self.fmt_num1 = self.wb.add_format({'num_format': '#,##0'})
        self.fmt_num1b = self.wb.add_format({'num_format': '#,##0',
                                             'bold': True})
        self.fmt_num2 = self.wb.add_format({'num_format': '#,##0.0'})
        self.fmt_pct = self.wb.add_format({'num_format': '0.0%'})
        
        self._writecf()
        self._writeloan()
        
        self.wb.close()
    
    def _writecf(self):
        # New Worksheet
        ws = self.wb.add_worksheet("cashflow")
        ws.write_string(0, 0, "Cash Flow", self.fmt_bold)
        col = 0
        row = 3
        
        # Write Index
        ws.write_column(row+2, col, idx.index, self.fmt_date)
        col += 1
        
        # Write OprtgAcc Balance
        ws.write_string(row, col, "운영계좌", self.fmt_bold)
        ws.write_string(row+1, col, "기초잔액", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.bal_strt, self.fmt_num1b)
        col += 1
        
        # Write CashIn
        ws.write_string(row, col, "CashIn", self.fmt_bold)
        ws.write_string(row+1, col, "Equity", self.fmt_bold)
        ws.write_column(row+2, col, equity.ntnl.df.amt_sub, self.fmt_num1)
        col += 1
        
        ws.write_string(row+1, col, "LoanTrA", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.ntnl.df.amt_sub, self.fmt_num1)
        col += 1
        
        ws.write_string(row+1, col, "LoanTrB", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.ntnl.df.amt_sub, self.fmt_num1)
        col += 1
        
        ws.write_string(row+1, col, "Sales", self.fmt_bold)
        ws.write_column(row+2, col, sales.df.amt_sub, self.fmt_num1)
        col += 1
        
        # Write Repayment
        ws.write_string(row, col, "Repayment", self.fmt_bold)
        
        ws.write_string(row+1, col, "LoanTrA", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.ntnl.df.amt_add, self.fmt_num1)
        col += 1
        
        ws.write_string(row+1, col, "LoanTrB", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.ntnl.df.amt_add, self.fmt_num1)
        col += 1
        
        # Write OprtgAcc Amount_add
        ws.write_string(row, col, "운영계좌", self.fmt_bold)
        ws.write_string(row+1, col, "현금유입", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.amt_add, self.fmt_num1b)
        col += 1
        
        # Write CashOut
        ws.write_string(row, col, "조달비용", self.fmt_bold)
        cstlst = fnccst.lfkey("account", return_val="dict")
        for dct in cstlst:
            ws.write_string(row+1, col, dct["byname"], self.fmt_bold)
            ws.write_column(row+2, col, dct["account"].df.amt_add.values, self.fmt_num1)
            col += 1
            
        ws.write_string(row, col, "금융비용", self.fmt_bold)
        
        ws.write_string(row+1, col, "TrA_fee", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.fee.df.amt_add, self.fmt_num1)
        col += 1
        
        ws.write_string(row+1, col, "TrB_fee", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.fee.df.amt_add, self.fmt_num1)
        col += 1
        
        ws.write_string(row+1, col, "TrA_IR", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.IR.df.amt_add, self.fmt_num1)
        col += 1
        
        ws.write_string(row+1, col, "TrB_IR", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.IR.df.amt_add, self.fmt_num1)
        col += 1

        for key, item in cost._dct.items():
            cstlst = cost.lfkey("account", return_val="dict", dct_ipt=item)
            ws.write_string(row, col, item["byname"], self.fmt_bold)
            for dct in cstlst:
                #ws.write_string(row, col, key, self.fmt_bold)
                ws.write_string(row+1, col, dct["byname"], self.fmt_bold)
                ws.write_column(row+2, col, dct["account"].df.amt_add.values, self.fmt_num1)
                col += 1
        
        # Write Equity Repayment
        ws.write_string(row, col, "Repayment", self.fmt_bold)
        
        ws.write_string(row+1, col, "Equity", self.fmt_bold)
        ws.write_column(row+2, col, equity.ntnl.df.amt_add, self.fmt_num1)
        col += 1
        
        # Write OprtgAcc Amount_sub
        ws.write_string(row, col, "운영계좌", self.fmt_bold)
        ws.write_string(row+1, col, "현금유출", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.amt_sub, self.fmt_num1b)
        col += 1
        
        # Write OprtgAcc Balance_end
        ws.write_string(row, col, "운영계좌", self.fmt_bold)
        ws.write_string(row+1, col, "기말잔액", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.bal_end, self.fmt_num1b)
        col += 1
        
        
    def _writeloan(self):
        # New Worksheet
        ws = self.wb.add_worksheet("loan")
        ws.write_string(0, 0, "Loan", self.fmt_bold)
        col = 0
        row = 3
        
        # Write Index
        ws.write_column(row+2, col, idx.index, self.fmt_date)
        col += 1
        
        # Write TrA
        ws.write_string(row-1, col, "Loan TrA", self.fmt_bold)
        
        ws.write_string(row, col, "TrA_notional", self.fmt_bold)
        ws.write_string(row+1, col, "sub_scdd", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.ntnl.df.sub_scdd, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "add_scdd", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.ntnl.df.add_scdd, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.ntnl.df.amt_sub, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.ntnl.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.ntnl.df.bal_end, self.fmt_num1)
        col += 1

        ws.write_string(row, col, "TrA_fee", self.fmt_bold)
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.fee.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.fee.df.bal_end, self.fmt_num1)
        col += 1
        
        ws.write_string(row, col, "TrA_IR", self.fmt_bold)
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.IR.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.IR.df.bal_end, self.fmt_num1)
        col += 1
        
        ws.write_string(row, col, "TrA_sum", self.fmt_bold)
        ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.df.amt_sub, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.tra.df.bal_end, self.fmt_num1)
        col += 1

        # Write TrB
        ws.write_string(row-1, col, "Loan TrB", self.fmt_bold)
        
        ws.write_string(row, col, "TrB_notional", self.fmt_bold)
        ws.write_string(row+1, col, "sub_scdd", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.ntnl.df.sub_scdd, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "add_scdd", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.ntnl.df.add_scdd, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.ntnl.df.amt_sub, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.ntnl.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.ntnl.df.bal_end, self.fmt_num1)
        col += 1
        
        ws.write_string(row, col, "TrB_fee", self.fmt_bold)
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.fee.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.fee.df.bal_end, self.fmt_num1)
        col += 1
        
        ws.write_string(row, col, "TrB_IR", self.fmt_bold)
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.IR.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.IR.df.bal_end, self.fmt_num1)
        col += 1
        
        ws.write_string(row, col, "TrB_sum", self.fmt_bold)
        ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.df.amt_sub, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, loan.trb.df.bal_end, self.fmt_num1)
        col += 1
        
        # Write Equity
        ws.write_string(row-1, col, "Equity", self.fmt_bold)
        ws.write_string(row, col, "Notional", self.fmt_bold)
        ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
        ws.write_column(row+2, col, equity.df.amt_sub, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, equity.df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, equity.df.bal_end, self.fmt_num1)
        col += 1
        
        ws.write_string(row, col, "운영비유입", self.fmt_bold)
        ws.write_string(row+1, col, "amt_add", self.fmt_bold)
        ws.write_column(row+2, col, cost.oprtgcst["account"].df.amt_add, self.fmt_num1)
        col += 1
        ws.write_string(row+1, col, "bal_end", self.fmt_bold)
        ws.write_column(row+2, col, cost.oprtgcst["account"].df.bal_end, self.fmt_num1)
        col += 1
        
        
        