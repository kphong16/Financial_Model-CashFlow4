#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 17:41:35 2021

@author: KP_Hong
"""

import xlsxwriter
from datetime import datetime
from cafle import Write

# Get Attributes from Main
idx     = None
equity  = None
#brgl    = None
loan    = None
sales   = None
#brgcst  = None
loancst  = None
cost    = None
acc     = None
# ovw     = None


class WriteCF(object):
    def __init__(self, file_adrs, data):
        self.file_adrs  = file_adrs
        self.data       = data
        self.wb         = Write(file_adrs)
        
        self._writecf()
        #self._writeloan()
        #self._writecst()
        
        self.wb.close()
        
    def _writecf(self):
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("cashflow")
        idx = self.data["idx"].idx
        oprtg = self.data["acc"].oprtg
        equity = self.data["equity"].equity
        fund = self.data["fund"].loan
        fundcst = self.data["fundcst"]
        loan = self.data["loan"].loan
        loancst = self.data["loancst"]
        mrtg = self.data["mrtg"].loan
        mrtgcst = self.data["mrtgcst"]
        sales = self.data["sales"].sales
        cost = self.data["cost"]
        
        ws.set_column(0, 0, 12)
        ws.write(0, 0, "CASH FLOW", wb.bold)
        ws.write(1, 0, "Written at: " + wb.now)
        ws.write(2, 0, self.file_adrs)
        
        row = 5
        col = 0
        
        # Write Index
        ws.write_column(row+2, col, idx.index, wb.date)
        col += 1
        
        # Write OprtgAcc Balance        
        tmpfmt = [wb.bold, wb.bold, wb.num]
        tmpdct = {"운영_기초"     : {"기초잔액": oprtg.df.bal_strt},
                  "CashIn"      : wb.extnddct(
                                  {"Equity" : equity.ntnl.df.amt_sub},
                                  {"Fund"   : fund.cmn.ntnl.df.amt_sub},
                                  {"Loan_"+key: item.ntnl.df.amt_sub for key, item in loan.dct.items()},
                                  {"Mrtg_"+key: item.ntnl.df.amt_sub for key, item in mrtg.dct.items()},
                                  {"Sales"  : sales.acc.df.amt_sub}
                                  ),
                  "상환_loan"    : wb.extnddct(
                                  {"Loan_"+key: item.ntnl.df.amt_add for key, item in loan.dct.items()},
                                  {"Mrtg_"+key: item.ntnl.df.amt_add for key, item in mrtg.dct.items()},
                                  {"Fund"   : fund.cmn.ntnl.df.amt_add}
                                  ),
                  "운영_유입"     : {"현금유입": oprtg.df.amt_add},
                  "조달비용"      : wb.extnddct(
                                  {item.acc.title: item.acc.df.amt_add for key, item in loancst.dct.items()},
                                  {item.acc.title: item.acc.df.amt_add for key, item in mrtgcst.dct.items()},
                                  {item.acc.title: item.acc.df.amt_add for key, item in fundcst.dct.items()}
                                  ),
                  "금융비용"      : wb.extnddct(
                                  {"Fee_"+key: item.fee.df.amt_add for key, item in loan.dct.items()},
                                  {"IR_"+key: item.IR.df.amt_add for key, item in loan.dct.items()},
                                  {"Fob_"+key: item.fob.df.amt_add for key, item in loan.dct.items() if item.rate_fob > 0}),
                  "담보대출"      : wb.extnddct(
                                  {"Fee_"+key: item.fee.df.amt_add for key, item in mrtg.dct.items()},
                                  {"IR_"+key: item.IR.df.amt_add for key, item in mrtg.dct.items()},
                                  {"Fob_"+key: item.fob.df.amt_add for key, item in mrtg.dct.items() if item.rate_fob > 0}),
                  "펀드배당"      : wb.extnddct(
                                  {"Fee_"+key: item.fee.df.amt_add for key, item in fund.dct.items()},
                                  {"IR_"+key: item.IR.df.amt_add for key, item in fund.dct.items()},
                                  {"Fob_"+key: item.fob.df.amt_add for key, item in fund.dct.items() if item.rate_fob > 0}),
                  }
        # Write Operating Costs
        tmpdct = wb.extnddct(tmpdct, 
                 {key: {key2: item2.acc.df.amt_add for key2, item2 in item.dct.items()}
                  for key, item in cost.dct.items()
                  }
                 )
        tmpdct = wb.extnddct(tmpdct,
                 {"상환_equity"  : {"Equity" : equity.ntnl.df.amt_add},
                  "운영_유출"  : {"현금유출" : oprtg.df.amt_sub},
                  "운영_기말"  : {"기말잔액" : oprtg.df.bal_end}
                  }
                 )
        wb.write_dct_col("cashflow", row, col, tmpdct, tmpfmt)
        
        
        
    """ 
        # Write FundAcc Balance_end
        col += 1
        ws.write_string(row, col, "펀드계좌", self.fmt_bold)
        ws.write_string(row+1, col, "기초잔액", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.bal_strt, self.fmt_num1b)
        col += 1
        ws.write_string(row+1, col, "현금유입", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.amt_add, self.fmt_num1b)
        col += 1
        ws.write_string(row+1, col, "현금유출", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.amt_sub, self.fmt_num1b)
        col += 1
        ws.write_string(row+1, col, "기말잔액", self.fmt_bold)
        ws.write_column(row+2, col, acc.oprtg.df.bal_end, self.fmt_num1b)
        col += 1
        
        
    def _writeloan(self):
        # New Worksheet
        ws = self.wb.add_worksheet("loan")
        ws.set_column(0, 0, 12)
        ws.write_string(0, 0, "LOAN", self.fmt_bold)
        ws.write_string(1, 0, "Written at: " + self.datetime)
        ws.write_string(2, 0, self.file_adrs)
        col = 0
        row = 6
        
        # Write Index
        ws.write_column(row+2, col, idx.index, self.fmt_date)
        col += 1
        
        
        for rnk in sorted(brgl.rnk, reverse=False):
            ws.write_string(row-1, col, "BrgL_"+brgl[rnk].title, self.fmt_bold)
            ws.write_string(row, col, "Notional_"+brgl[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "sub_scdd", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].ntnl.df.sub_scdd, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "add_scdd", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].ntnl.df.add_scdd, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].ntnl.df.amt_sub, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].ntnl.df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].ntnl.df.bal_end, self.fmt_num1)
            col += 1
    
            ws.write_string(row, col, "Fee_"+brgl[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].fee.df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].fee.df.bal_end, self.fmt_num1)
            col += 1
            
            ws.write_string(row, col, "IR_"+brgl[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].IR.df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].IR.df.bal_end, self.fmt_num1)
            col += 1
            
            if brgl[rnk].rate_fob > 0:
                ws.write_string(row, col, "Fob_"+brgl[rnk].title, self.fmt_bold)
                ws.write_string(row+1, col, "amt_add", self.fmt_bold)
                ws.write_column(row+2, col, brgl[rnk].fob.df.amt_add, self.fmt_num1)
                col += 1
                ws.write_string(row+1, col, "bal_end", self.fmt_bold)
                ws.write_column(row+2, col, brgl[rnk].fob.df.bal_end, self.fmt_num1)
                col += 1
            
            ws.write_string(row, col, "Sum_"+brgl[rnk].title, self.fmt_bold)
            ws.write_string(row+1, col, "amt_sub", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].df.amt_sub, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "amt_add", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].df.amt_add, self.fmt_num1)
            col += 1
            ws.write_string(row+1, col, "bal_end", self.fmt_bold)
            ws.write_column(row+2, col, brgl[rnk].df.bal_end, self.fmt_num1)
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
            
            if loan[rnk].rate_fob > 0:
                ws.write_string(row, col, "Fob_"+loan[rnk].title, self.fmt_bold)
                ws.write_string(row+1, col, "amt_add", self.fmt_bold)
                ws.write_column(row+2, col, loan[rnk].fob.df.amt_add, self.fmt_num1)
                col += 1
                ws.write_string(row+1, col, "bal_end", self.fmt_bold)
                ws.write_column(row+2, col, loan[rnk].fob.df.bal_end, self.fmt_num1)
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
        
        
    def _writecst(self):
        # New Worksheet
        ws = self.wb.add_worksheet("loancst")
        ws.set_column(0, 1, 16)
        ws.write_string(0, 0, "Financing and Costs", self.fmt_bold)
        ws.write_string(1, 0, "Written at: " + self.datetime)
        ws.write_string(2, 0, self.file_adrs)
        col = 0
        row = 5
        ttl_sum = [0, 0, 0, 0]
        
        idx_intl = idx[0]
        idx_loan = slice(idx.loan[0], idx.loan[-1])
        idx_rsrv = slice(idx[-2], idx[-1])
        
        
        #### WRITE FINANCING ####
        ws.write_string(row, col, "FINANCING", self.fmt_bold)
        row += 1
        tmp_lst = ["일시대", "한도대", "대출금", "IR", "Fee", "All-in", "FoB", "", "IR_amt", "Fee_amt"]
        ws.write_row(row, col+2, tmp_lst, self.fmt_bold)
        row += 1
        
        
        # Write Bridge
        ws.write_string(row, col, "Bridge", self.fmt_bold)
        for rnk in sorted(brgl.rnk, reverse=False):
            ws.write_string(row, col+1, brgl[rnk].title, self.fmt_bold)
            ws.write_number(row, col+2, brgl[rnk].amt_intl, self.fmt_num1)
            ws.write_number(row, col+3, brgl[rnk].amt_ntnl - brgl[rnk].amt_intl, self.fmt_num1)
            ws.write_number(row, col+4, brgl[rnk].amt_ntnl, self.fmt_num1)
            ws.write_number(row, col+5, brgl[rnk].rate_IR, self.fmt_pct)
            ws.write_number(row, col+6, brgl[rnk].rate_fee, self.fmt_pct)
            ws.write_number(row, col+7, brgl[rnk].rate_allin, self.fmt_pct)
            ws.write_number(row, col+8, brgl[rnk].rate_fob, self.fmt_pct)
            ws.write_number(row, col+10, brgl[rnk].amt_IR, self.fmt_num1)
            ws.write_number(row, col+11, brgl[rnk].amt_fee, self.fmt_num1)
            row += 1
        
        
        # Write loan
        ws.write_string(row, col, "Loan", self.fmt_bold)
        for rnk in sorted(loan.rnk, reverse=False):
            ws.write_string(row, col+1, loan[rnk].title, self.fmt_bold)
            ws.write_number(row, col+2, loan[rnk].amt_intl, self.fmt_num1)
            ws.write_number(row, col+3, loan[rnk].amt_ntnl - loan[rnk].amt_intl, self.fmt_num1)
            ws.write_number(row, col+4, loan[rnk].amt_ntnl, self.fmt_num1)
            ws.write_number(row, col+5, loan[rnk].rate_IR, self.fmt_pct)
            ws.write_number(row, col+6, loan[rnk].rate_fee, self.fmt_pct)
            ws.write_number(row, col+7, loan[rnk].rate_allin, self.fmt_pct)
            ws.write_number(row, col+8, loan[rnk].rate_fob, self.fmt_pct)
            ws.write_number(row, col+10, loan[rnk].amt_IR, self.fmt_num1)
            ws.write_number(row, col+11, loan[rnk].amt_fee, self.fmt_num1)
            row += 1
            
        # Write sum of loan
        ws.write_string(row, col+1, "Sum", self.fmt_bold)
        sumintl = sum([val.amt_intl for val in loan.ttl.dct.values()])
        sumntnl = sum([val.amt_ntnl for val in loan.ttl.dct.values()])
        sumrsdl = sumntnl - sumintl
        ws.write_number(row, col+2, sumintl, self.fmt_num1b)
        ws.write_number(row, col+3, sumrsdl, self.fmt_num1b)
        ws.write_number(row, col+4, sumntnl, self.fmt_num1b)
        ws.write_number(row, col+6, loan.rate_arng, self.fmt_pct)
        ws.write_number(row, col+7, loan.allin, self.fmt_pct)
        
        sumIR = sum([val.amt_IR for val in loan.ttl.dct.values()])
        sumfee = sum([val.amt_fee for val in loan.ttl.dct.values()])
        ws.write_number(row, col+10, sumIR, self.fmt_num1b)
        ws.write_number(row, col+11, sumfee, self.fmt_num1b)
        row += 1
        
        # Write equity
        ws.write_string(row, col, "Equity", self.fmt_bold)
        ws.write_number(row, col+2, equity.amt_intl, self.fmt_num1)
        ws.write_number(row, col+3, equity.amt_ntnl - equity.amt_intl, self.fmt_num1)
        ws.write_number(row, col+4, equity.amt_ntnl, self.fmt_num1)
        row += 1
        
        # Write total costs
        ws.write_string(row, col, "Total", self.fmt_bold)
        ws.write_number(row, col+2, sumintl + equity.amt_intl, self.fmt_num1b)
        ws.write_number(row, col+3, sumrsdl + equity.amt_ntnl - equity.amt_intl, self.fmt_num1b)
        ws.write_number(row, col+4, sumntnl + equity.amt_ntnl, self.fmt_num1b)
        row += 1
        
        #### WRITE COSTS ####
        row += 3
        ws.write_string(row, col, "COSTS", self.fmt_bold)
        row += 1
        
        tmp_txt = ["총금액", "기투입", "PF사업비", "유보사업비"]
        ws.write_row(row, col+2, tmp_txt, self.fmt_bold)
        row += 1
        
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
        cstlst = loancst.lfkey("account", return_val="dict")
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
            
        for rnk in sorted(loan.rnk, reverse=False):
            if loan[rnk].rate_fob > 0:
                ws.write_string(row, col+1, "Fob_"+loan[rnk].title, self.fmt_bold)
                lst_amt = loan[rnk].fob.df.amt_add
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
        
        
        # Write Bridge Cashout: Cost of Bridge Financing
        ws.write_string(row, col, "브릿지조달비용", self.fmt_bold)
        brglst = brgcst.lfkey("account", return_val="dict")
        sum_clct = [0, 0, 0, 0]
        for dct in brglst:
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
        ws.write_string(row, col, "브릿지금융비용", self.fmt_bold)
        
        sum_clct = [0, 0, 0, 0]
        for rnk in sorted(brgl.rnk, reverse=False):
            ws.write_string(row, col+1, "Fee_"+brgl[rnk].title, self.fmt_bold)
            lst_amt = brgl[rnk].fee.df.amt_add
            amt_ttl = sum(lst_amt)
            amt_intl = lst_amt[idx_intl]
            amt_loan = sum(lst_amt[idx_loan])
            amt_rsrv = sum(lst_amt[idx_rsrv])
            amt_clct = [amt_ttl, amt_intl, amt_loan, amt_rsrv]
            sum_clct = [i + j for i, j in zip(sum_clct, amt_clct)]
            ws.write_row(row, col+2, amt_clct, self.fmt_num1)
            row += 1
            
        for rnk in sorted(brgl.rnk, reverse=False):
            ws.write_string(row, col+1, "IR_"+brgl[rnk].title, self.fmt_bold)
            lst_amt = brgl[rnk].IR.df.amt_add
            amt_ttl = sum(lst_amt)
            amt_intl = lst_amt[idx_intl]
            amt_loan = sum(lst_amt[idx_loan])
            amt_rsrv = sum(lst_amt[idx_rsrv])
            amt_clct = [amt_ttl, amt_intl, amt_loan, amt_rsrv]
            sum_clct = [i + j for i, j in zip(sum_clct, amt_clct)]
            ws.write_row(row, col+2, amt_clct, self.fmt_num1)
            row += 1
        
        for rnk in sorted(brgl.rnk, reverse=False):
            if brgl[rnk].rate_fob > 0:
                ws.write_string(row, col+1, "Fob_"+brgl[rnk].title, self.fmt_bold)
                lst_amt = brgl[rnk].fob.df.amt_add
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
    """
        