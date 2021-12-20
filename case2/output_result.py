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
        self._writecst()
        
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
        
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row+1, col, "Loan_"+loan[rnk].title, self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].ntnl.df.amt_sub, self.fmt_num1)
            col += 1
        
        ws.write_string(row+1, col, "Sales", self.fmt_bold)
        ws.write_column(row+2, col, sales.df.amt_sub, self.fmt_num1)
        col += 1
        
        # Write Repayment
        ws.write_string(row, col, "Repayment", self.fmt_bold)
        
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row+1, col, "Loan_"+loan[rnk].title, self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].ntnl.df.amt_add, self.fmt_num1)
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
        
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row+1, col, "Fee_"+loan[rnk].title, self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].fee.df.amt_add, self.fmt_num1)
            col += 1
            
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row+1, col, "IR_"+loan[rnk].title, self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].IR.df.amt_add, self.fmt_num1)
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
        
        # Write Loan
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row-1, col, "Loan_"+loan[rnk].title, self.fmt_bold)
            ws.write_string(row, col, "Notional_"+loan[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "sub_scdd", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].ntnl.df.sub_scdd, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "add_scdd", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].ntnl.df.add_scdd, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].ntnl.df.amt_sub, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].ntnl.df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].ntnl.df.bal_end, self.fmt_num1)
            col += 1
    
            ws.write_string(row, col, "Fee_"+loan[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].fee.df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].fee.df.bal_end, self.fmt_num1)
            col += 1
            
            ws.write_string(row, col, "IR_"+loan[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].IR.df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].IR.df.bal_end, self.fmt_num1)
            col += 1
            
            ws.write_string(row, col, "Sum_"+loan[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].df.amt_sub, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, loan[rnk].df.bal_end, self.fmt_num1)
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
        
        
    def _writecst(self):
        # New Worksheet
        ws = self.wb.add_worksheet("cost")
        ws.write_string(0, 0, "Cost Balance", self.fmt_bold)
        col = 0
        row = 3
        ttl_sum = [0, 0, 0, 0]
        
        idx_intl = idx[0]
        idx_loan = slice(idx.loan[0], idx.loan[-1])
        idx_rsrv = slice(idx[-2], idx[-1])
        
        tmp_txt = ["총금액", "기투입", "PF사업비", "유보사업비"]
        ws.write_row(row-1, col+2, tmp_txt, self.fmt_bold)
        
        # Write Cashout: Operating Cost
        for key, item in cost._dct.items():
            cstlst = cost.lfkey("account", return_val="dict", dct_ipt=item)
            ws.write_string(row, col, item["byname"], self.fmt_bold)
            
            sum_clct = [0, 0, 0, 0]
            for dct in cstlst:
                #ws.write_string(row, col, key, self.fmt_bold)
                ws.write_string(row, col+1, dct["byname"], self.fmt_bold)
                amt_ttl = dct["amtttl"]
                amt_intl = dct["account"].df.amt_add[idx_intl]
                amt_loan = sum(dct["account"].df.amt_add[idx_loan])
                amt_rsrv = sum(dct["account"].df.amt_add[idx_rsrv])
                amt_clct = [amt_ttl, amt_intl, amt_loan, amt_rsrv]
                sum_clct = [i + j for i, j in zip(sum_clct, amt_clct)]
                ws.write_row(row, col+2, amt_clct, self.fmt_num1)
                row += 1
            ws.write_string(row, col+1, "sum", self.fmt_bold)
            ws.write_row(row, col+2, sum_clct, self.fmt_num1b)
            ttl_sum = [i + j for i, j in zip(ttl_sum, sum_clct)]
            row += 1
                
        # Write Cashout: Cost of Financing
        ws.write_string(row, col, "조달비용", self.fmt_bold)
        cstlst = fnccst.lfkey("account", return_val="dict")
        sum_clct = [0, 0, 0, 0]
        for dct in cstlst:
            ws.write_string(row, col+1, dct["byname"], self.fmt_bold)
            lst_amt = dct["account"].df.amt_add
            amt_ttl = sum(lst_amt)
            amt_intl = lst_amt[idx_intl]
            amt_loan = sum(lst_amt[idx_loan])
            amt_rsrv = sum(lst_amt[idx_rsrv])
            amt_clct = [amt_ttl, amt_intl, amt_loan, amt_rsrv]
            sum_clct = [i + j for i, j in zip(sum_clct, amt_clct)]
            ws.write_row(row, col+2, amt_clct, self.fmt_num1)
            row += 1
        ws.write_string(row, col+1, "sum", self.fmt_bold)
        ws.write_row(row, col+2, sum_clct, self.fmt_num1b)
        ttl_sum = [i + j for i, j in zip(ttl_sum, sum_clct)]
        row += 1
        
        # Write Cashout: Interest Rate and Loan Fee Cost
        ws.write_string(row, col, "금융비용", self.fmt_bold)
        
        sum_clct = [0, 0, 0, 0]
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row, col+1, "Fee_"+loan[rnk].title, self.fmt_bold)
            lst_amt = loan[rnk].fee.df.amt_add
            amt_ttl = sum(lst_amt)
            amt_intl = lst_amt[idx_intl]
            amt_loan = sum(lst_amt[idx_loan])
            amt_rsrv = sum(lst_amt[idx_rsrv])
            amt_clct = [amt_ttl, amt_intl, amt_loan, amt_rsrv]
            sum_clct = [i + j for i, j in zip(sum_clct, amt_clct)]
            ws.write_row(row, col+2, amt_clct, self.fmt_num1)
            row += 1
            
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row, col+1, "IR_"+loan[rnk].title, self.fmt_bold)
            lst_amt = loan[rnk].IR.df.amt_add
            amt_ttl = sum(lst_amt)
            amt_intl = lst_amt[idx_intl]
            amt_loan = sum(lst_amt[idx_loan])
            amt_rsrv = sum(lst_amt[idx_rsrv])
            amt_clct = [amt_ttl, amt_intl, amt_loan, amt_rsrv]
            sum_clct = [i + j for i, j in zip(sum_clct, amt_clct)]
            ws.write_row(row, col+2, amt_clct, self.fmt_num1)
            row += 1
                    
        ws.write_string(row, col+1, "sum", self.fmt_bold)
        ws.write_row(row, col+2, sum_clct, self.fmt_num1b)
        ttl_sum = [i + j for i, j in zip(ttl_sum, sum_clct)]
        row += 1
        
        # Write Total Costs
        ws.write_string(row, col, "Total Sum", self.fmt_bold)
        ws.write_row(row, col+2, ttl_sum, self.fmt_num1b)
        row += 1
        