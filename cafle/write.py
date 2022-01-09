#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 17:41:35 2021

@author: KP_Hong
"""

import xlsxwriter
from datetime import datetime

__all__ = ['Write']

class Write(object):
    def __init__(self, file_adrs):
        self.file_adrs = file_adrs
        self.wb = xlsxwriter.Workbook(self.file_adrs)
        self.ws = {}
        
        
    # Text Format
    def fmtnum(self, fmt, **kwargs):
        """
        example of fmt: 'yyyy-mm-dd', '#,##0', '#,##0.0', '0.0%'
        kwargs example: bold=True
        """
        tmpdct = dict({'num_format': fmt}, **kwargs)
        return self.wb.add_format(tmpdct)
    
    @property
    def bold(self):
        return self.wb.add_format({'bold': True})
        
    @property
    def num(self):
        return self.wb.add_format({'num_format': '#,##0'})
        
    @property
    def numb(self):
        return self.wb.add_format({'num_format': '#,##0', 'bold': True})
        
    @property
    def pct(self):
        return self.wb.add_format({'num_format': '0.0%'})
        
    @property
    def pct2(self):
        return self.wb.add_format({'num_format': '0.00%'})
        
    @property
    def date(self):
        return self.wb.add_format({'num_format': 'yyyy-mm-dd'})
    
    @property    
    def now(self):
        return datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        
    
    # Close Workbook
    def close(self):
        self.wb.close()
        return True
        
    
    # Add Worksheet
    def add_ws(self, wsname):
        self.ws[wsname] = self.wb.add_worksheet(wsname)
        return self.ws[wsname]
        
        
    # Write Row
    def write_row(self, wsname, row, col, data, fmt=None):
        for val in data:
            self.ws[wsname].write_row(row, col, val, fmt)
            row += 1
        return (row, col)
        
    # Write Column
    def write_col(self, wsname, row, col, data, fmt=None):
        for val in data:
            self.ws[wsname].write_column(row, col, val, fmt)
            col += 1
        return (row, col)
        
    # Write Dictionary
    def write_dct_col(self, wsname, row, col, datadct, fmtlst=None):
        ws = self.ws[wsname]
        for key, item in datadct.items():
            if type(item) is not dict:
                ws.write(row, col, key, fmtlst[0])
                ws.write_column(row+1, col, item, fmtlst[1])
                col += 1
            if type(item) is dict:
                ws.write(row, col, key, fmtlst[0])
                col = self.write_dct_col(wsname, row+1, col, item, fmtlst[1:])
        return col
    
    # Make Dictionary of Loan
    def dct_loan(self, ln):
        tmpdct = {}
        tmpdct["Notional_" + ln.title] = \
            {"scd_out": ln.ntnl._df.scd_out,
             "scd_in": ln.ntnl._df.scd_in,
             "amt_out" : ln.ntnl._df.amt_out,
             "amt_in" : ln.ntnl._df.amt_in,
             "bal_end" : ln.ntnl._df.bal_end}
        
        tmpdct["IR_" + ln.title] = \
            {"amt_in" : ln.IR._df.amt_in,
             "bal_end" : ln.IR._df.bal_end}
        if 'fee' in ln.fnkey:
            tmpdct["Fee_" + ln.title] = \
                {"amt_in" : ln.fee._df.amt_in,
                 "bal_end" : ln.fee._df.bal_end}
        if 'fob' in ln.fnkey:
            tmpdct["Fob_" + ln.title] = \
                {"amt_in" : ln.fob._df.amt_in,
                 "bal_end" : ln.fob._df.bal_end}
        return tmpdct

        
    # Write Val
    def write(self, wsname, row, col, val, fmt=None):
        self.ws[wsname].write(row, col, val, fmt)
    
    # Extend List
    def extndlst(self, lst, *arg):
        for val in arg:
            lst.extend(val)
        return lst
    
    def extnddct(self, dct, *arg):
        for val in arg:
            dct = dict(dct, **val)
        return dct
    
    
    
    
    
    
    
    
    
    
    
    