import pandas as pd
import numpy as np
from pandas import Series, DataFrame

from .genfunc import *
from .index import *
from .account import *

__all__ = ['Cost']

class Cost:
    def __init__(self,
                 index, # basic index class
                 idxcst = None, # cost index class
                 ):
        # Input index
        self.index = index
        if idxcst == None:
            idxcst = index
        self.idxcst = idxcst
        
        self.title = []
        self.byname = {}
        self._dct = {}
        
        self._intlz()
        
    def __len__(self):
        return len(self.title)
        
    def _intlz(self):
        pass
        
    def inptcst(self,
                title, # str
                byname = None, # str
                scddidx = None, # list
                scddamt = None, # list
                scdddf = None, # DataFrame([[scddidx, scddamt]])
                ):
        if title not in self.title:
            self.title.append(title)
            tmp_acc = Account(self.index, flatten_tuple(title))
            self._dct[title] = tmp_acc
            self.byname[title] = byname
        
        if scddidx is None or scddamt is None:
            tmp_dct = DataFrame(scdddf, columns=['scddidx', 'scddamt'])
            scddidx = tmp_dct.scddidx
            scddamt = tmp_dct.scddamt
        
        tmp_istnc = self._dct[title]
        tmp_istnc.addscdd(scddidx, scddamt)
        
        setattr(tmp_istnc, 'amt', tmp_istnc.add_scdd[:].sum())
        
    def dct(self, key=None):
        if key is None:
            return self._dct
        if type(key) is str:
            tmp_dct = {}
            for dct_key, dct_item in self._dct.items():
                if key in dct_key:
                    tmp_dct[dct_key[1]] = dct_item
            return tmp_dct
        if type(key) is tuple:
            for dct_key, dct_item in self._dct.items():
                if key == dct_key:
                    return dct_item
                    
    def __getitem__(self, key):
        if key == "all":
            return Merge(self._dct)
        if type(key) is str:
            tmp_dct = self.dct(key)
            return Merge(tmp_dct)
        if type(key) is tuple:
            tmp_dct = self.dct(key)
            return Merge(tmp_dct)
            
    def __getattr__(self, attr):
        return self.__dict__[attr]
            
            
def flatten_tuple(tpl, crit="_"):
    if type(tpl) == str:
        return tpl
    
    tmpval = ""
    for i, val in enumerate(tpl):
        if i == 0:
            tmpval += str(val)
        else:
            tmpval += crit
            tmpval += str(val)
    return tmpval
    