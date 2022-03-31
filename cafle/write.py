#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 17:41:35 2021

@author: KP_Hong
"""

import xlsxwriter
from datetime import datetime
from pandas import DataFrame
from cafle.genfunc import is_iterable, is_scalar
from collections import namedtuple

__all__ = ['Write', 'WriteWS', 'Cell']

class Cell:
    def __new__(cls, row, col):
        cell = namedtuple("Cell", ["row", "col"])
        return cell(row, col)


def depth_dct(dct):
    tlen = 0
    for item in dct.values():
        if type(item) is dict:
            tlen = max(depth_dct(item), tlen)
        elif is_iterable(item):
            tlen = max(len(item), tlen)
        else:
            tlen = max(1, tlen)
    return 1 + tlen

class Write(object):
    def __init__(self, file_adrs):
        self.file_adrs = file_adrs
        self.wb = xlsxwriter.Workbook(self.file_adrs)
        self.ws = {}
        
    # Close workbook
    def close(self):
        self.wb.close()
        return True
        
    # Add worksheet
    def add_ws(self, wsname):
        self.ws[wsname] = self.wb.add_worksheet(wsname)
        return self.ws[wsname]
        
    # Write val
    def write(self, cell, val, fmt=None, wsname=None, drtn='row'):
        self.rtnws(wsname).write(cell.row, cell.col, val, fmt)
        row = cell.row
        col = cell.col
        
        if drtn == "row":
            row += 1
        elif drtn == "col":
            col += 1
        return Cell(row, col)
    
    # Write row
    def write_row(self, cell, data, fmt=None, wsname=None, drtn='row'):
        row = cell.row
        col = cell.col
        dlen = 0
        
        if not is_iterable(fmt):
            fmt = [fmt] * len(data)
                
        if is_iterable(data[0]):
            for val, _fmt in zip(data, fmt):
                self.rtnws(wsname).write_row(row, col, val, _fmt)
                dlen = max(len(val), dlen)
                row += 1
        elif not is_iterable(data[0]):
            _col = col
            for val, _fmt in zip(data, fmt):
                self.rtnws(wsname).write(row, _col, val, _fmt)
                _col += 1
            dlen = max(len(data), dlen)
            row += 1
            
        if drtn=='col':
            row = cell.row
            col = cell.col + dlen
        return Cell(row, col)
        
    # Write column
    def write_col(self, cell, data, fmt=None, wsname=None, drtn='col'):
        row = cell.row
        col = cell.col
        dlen = 0
        
        if not is_iterable(fmt):
            fmt = [fmt] * len(data)
        
        if is_iterable(data[0]):
            for val, _fmt in zip(data, fmt):
                self.rtnws(wsname).write_column(row, col, val, _fmt)
                dlen = max(len(val), dlen)
                col += 1
        elif not is_iterable(data[0]):
            _row = row
            for val, _fmt in zip(data, fmt):
                self.rtnws(wsname).write(_row, col, val, _fmt)
                _row += 1
            dlen = max(len(data), dlen)
            col += 1
            
        if drtn == 'row':
            row = cell.row + dlen
            col = cell.col
        return Cell(row, col)
    
    # Write dictionary column
    def write_dct_col(self, cell, data, fmt=None, wsname=None, drtn='col'):
        row = cell.row
        col = cell.col
        fmtlst = []
        
        if is_iterable(fmt):
            if len(fmt) == 1:
                fmtlst = fmt * 2
            else:
                fmtlst = fmt
        else:
            fmtlst = [fmt] * 2
        
        for key, item in data.items():
            if type(item) is not dict:
                self.rtnws(wsname).write(row, col, key, fmtlst[0])
                if is_iterable(item):
                    self.rtnws(wsname).write_column(row+1, col, item, fmtlst[1])
                else:
                    self.rtnws(wsname).write(row+1, col, item, fmtlst[1])
                col += 1
            if type(item) is dict:
                self.rtnws(wsname).write(row, col, key, fmtlst[0])
                tcell = self.write_dct_col(Cell(row+1, col), item, fmtlst[1:], wsname, drtn='col')
                row = tcell.row - 1
                col = tcell.col
            
        if drtn == 'row':
            row = cell.row + depth_dct(data)
            col = cell.col
        return Cell(row, col)
        
            
    # Write Dictionary
    def write_dct_row(self, cell, data, fmt=None, wsname=None, drtn='row'):
        row = cell.row
        col = cell.col
        fmtlst = []
        
        if is_iterable(fmt):
            if len(fmt) == 1:
                fmtlst = fmt * 2
            else:
                fmtlst = fmt
        else:
            fmtlst = [fmt] * 2
            
        for key, item in data.items():
            if type(item) is not dict:
                self.rtnws(wsname).write(row, col, key, fmtlst[0])
                if is_iterable(item):
                    self.rtnws(wsname).write_row(row, col+1, item, fmtlst[1])
                else:
                    self.rtnws(wsname).write(row, col+1, item, fmtlst[1])
                row += 1
            if type(item) is dict:
                self.rtnws(wsname).write(row, col, key, fmtlst[0])
                tcell = self.write_dct_row(Cell(row, col+1), item, fmtlst[1:], wsname, drtn='row')
                row = tcell.row
                col = tcell.col - 1
        
        if drtn == 'col':
            row = cell.row
            col = cell.col + depth_dct(data)
        return Cell(row, col)
        
    # Write DataFrame
    def write_df_col(self, cell, data, fmt=None, wsname=None, drtn='row'):
        dfdict = data.to_dict('split')
        row = cell.row
        col = cell.col
        
        dfcollen = len(dfdict['columns'])
        dfidxlen = len(dfdict['index'])
        
        if isinstance(dfdict['columns'][0], tuple):
            dfcolno = len(dfdict['columns'][0])
        else:
            dfcolno = 1
            
        if isinstance(dfdict['index'][0], tuple):
            dfidxno = len(dfdict['index'][0])
        else:
            dfidxno = 1
        
        if not is_iterable(fmt):
            fmtlst = [fmt] * dfcollen
        else:
            fmtlst = fmt
            
        if dfcolno == 1:
            self.write_row(Cell(row, col+dfidxno), dfdict['columns'], None, wsname)
        elif dfcolno > 1:
            _row = row
            _col = col + dfidxno
            for valtpl in dfdict['columns']:
                self.write_col(Cell(_row, _col), valtpl, None, wsname)
                _col += 1
        
        if dfidxno == 1:
            self.write_col(Cell(row+dfcolno, col), dfdict['index'], None, wsname)
        elif dfidxno > 1:
            _row = row + dfcolno
            _col = col
            for valtpl in dfdict['index']:
                self.write_row(Cell(_row, _col), valtpl, None, wsname)
                _row += 1
        
        _row = row+dfcolno
        _col = col+dfidxno
        for valtpl in dfdict['data']:
            self.write_row(Cell(_row, _col), valtpl, fmtlst, wsname)
            _row += 1
            
        if drtn == 'col':
            row = cell.row
            col = cell.col + dfidxno + dfcollen
        elif drtn == 'row':
            row = cell.row + dfcolno + dfidxlen
            col = cell.col
        return Cell(row, col)
        
        
    # Make Dictionary of Loan
    def dct_loan(self, ln):
        tmpdct = {}
        tmpdct["Notional_" + ln.title] = \
            {"scd_out": ln.ntnl._df.scd_out,
             "scd_in": ln.ntnl._df.scd_in,
             "amt_out" : ln.ntnl._df.amt_out,
             "amt_in" : ln.ntnl._df.amt_in,
             "bal_end" : ln.ntnl._df.bal_end}
        
        if 'IR' in ln.keys:
            tmpdct["IR_" + ln.title] = \
                {"amt_in" : ln.IR._df.amt_in,
                 "bal_end" : ln.IR._df.bal_end}
        if 'fee' in ln.keys:
            tmpdct["Fee_" + ln.title] = \
                {"amt_in" : ln.fee._df.amt_in,
                 "bal_end" : ln.fee._df.bal_end}
        if 'fob' in ln.keys:
            tmpdct["Fob_" + ln.title] = \
                {"amt_in" : ln.fob._df.amt_in,
                 "bal_end" : ln.fob._df.bal_end}
        return tmpdct

    # Make Dictionary of Loan
    def dctprt_loan(self, ln):
        tmpdct = {}
        tmpdct["Notional_" + ln.title] = \
            {"인출한도": ln.ntnl._df.scd_out,
             "상환예정": ln.ntnl._df.scd_in,
             "인출금액": ln.ntnl._df.amt_out,
             "상환금액": ln.ntnl._df.amt_in,
             "대출잔액": ln.ntnl._df.bal_end}

        if 'IR' in ln.keys:
            tmpdct["IR_" + ln.title] = \
                {"이자금액": ln.IR._df.amt_in,
                 "누적이자": ln.IR._df.bal_end}
        if 'fee' in ln.keys:
            tmpdct["Fee_" + ln.title] = \
                {"수수료금액": ln.fee._df.amt_in,
                 "누적수수료": ln.fee._df.bal_end}
        if 'fob' in ln.keys:
            tmpdct["미인출_" + ln.title] = \
                {"미인출수수료": ln.fob._df.amt_in,
                 "누적미인출": ln.fob._df.bal_end}
        return tmpdct

    # Extend List
    def extndlst(self, lst, *arg):
        for val in arg:
            lst.extend(val)
        return lst
    
    # Extend Dictionary
    def extnddct(self, dct, *arg):
        for val in arg:
            dct = dict(dct, **val)
        return dct
    
    # Return worksheet
    def rtnws(self, wsname):
        if isinstance(wsname, str):
            return self.ws[wsname]
        elif isinstance(wsname, xlsxwriter.worksheet.Worksheet):
            return wsname
        
    # Text Format
    def fmtnum(self, fmt, **kwargs):
        """
        example of fmt: 'yyyy-mm-dd', '#,##0', '#,##0.0', '0.0%'
        kwargs example: bold=True
        """
        tmpdct = dict({'num_format': fmt, **kwargs})
        return self.wb.add_format(tmpdct)
    
    @property
    def nml(self):
        return self.wb.add_format({'bold': False})
    
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
    def month(self):
        return self.wb.add_format({'num_format': '#,##0"개월"'})
    
    @property
    def now(self):
        return datetime.now().strftime('%Y.%m.%d %H:%M:%S')


class WriteWS(Write):
    def __init__(self, ws, cell):
        self.ws = ws
        self.cell = cell

    def __call__(self, data, fmt=None, valdrtn='row', drtn='row'):
        if not is_iterable(data):
            self.cell = self.write(self.cell, data, fmt, self.ws, drtn)
        elif isinstance(data, DataFrame):
            if valdrtn == 'row':
                raise ValueError("function for row option is not written.")
            elif valdrtn == 'col':
                self.cell = self.write_df_col(self.cell, data, fmt, self.ws, drtn)
        elif is_iterable(data) and not isinstance(data, dict):
            if valdrtn == 'row':
                self.cell = self.write_row(self.cell, data, fmt, self.ws, drtn)
            elif valdrtn == 'col':
                self.cell = self.write_col(self.cell, data, fmt, self.ws, drtn)
        elif isinstance(data, dict):
            if valdrtn == 'row':
                self.cell = self.write_dct_row(self.cell, data, fmt, self.ws, drtn)
            if valdrtn == 'col':
                self.cell = self.write_dct_col(self.cell, data, fmt, self.ws, drtn)
        return self.cell
    
    def setcell(self, row=None, col=None):
        if isinstance(row, tuple):
            self.cell = row
            return None
        
        _row = self.cell.row
        _col = self.cell.col
        if row is not None:
            _row = row
        if col is not None:
            _col = col
        self.cell = Cell(_row, _col)
        return None
    
    def nextcell(self, no=1, drtn='row'):
        _row = self.cell.row
        _col = self.cell.col
        if drtn=='row':
            _row += no
        elif drtn=='col':
            _col += no
        self.cell = Cell(_row, _col)
        return self.cell
        
    def dctdatalen(self, dct):
        _len = 0
        for key, item in dct.items():
            if is_iterable(item):
                _len = max(_len, len(item))
        return _len


        
        
        
        
        
        
        
        
        
        
        
    
    
    