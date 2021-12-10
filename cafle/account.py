import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from pandas.tseries.offsets import Day, MonthEnd
import datetime as dt
from datetime import datetime
from datetime import timedelta
from datetime import date
from functools import wraps

# import genfunc
# from index import Index
from .genfunc import *
from .index import Index, PrjtIndex

__all__ = ['Account', 'Merge', 'Intlz_accounts']

class Account(object):
    """
    PARAMETERS
    - index : Index class
    - title : string
    - tag : tuple of str
    - balstrt : default 0, amount which the balance starts
    - note : str
    ATTRIBUTES
    - df : Dataframe of data summary
    - _df : Dataframe of all data
    - add_scdd : get value of "add_scdd" column
      ex) Account.add_scdd[idx[0]]
    - add_scdd_cum : get value of "add_scdd_cum" column
    - sub_scdd : get value of "sub_scdd" column
    - sub_scdd_cum : get value of "sub_scdd_cum" column
    - bal_strt : get value of "bal_strt" column
    - amt_add : get value of "amt_add" column
    - amt_add_cum : get value of "amt_add_cum" column
    - amt_sub : get value of "amt_sub" column
    - amt_sub_cum : get value of "amt_sub_cum" column
    - bal_end : get value of "bal_end" column
    - add_rsdl_cum : get value of "add_rsdl_cum" column
    - sub_rsdl_cum : get value of "sub_rsdl_cum" column
    METHODS
    - send(index, amt, account) : Transfer amount to "account" account
    - addscdd(index, amt) : Input amt data on "add_scdd" column.
      ex) Account.addscdd(idx[0], 10_000)
      ex) Account.addscdd(idx[[1, 2]], [10_000, 20_000])
    - subscdd(index, amt) : Input amt data on "sub_scdd" column.
    - addamt(index, amt) : Input amt data on "amt_add" column.
    - subamt(index, amt): Input amt data on "amt_sub" column.
    - iptamt(index, amt) : Input amt data on "amt_add" or "amt_sub" column.
    """
    def __init__(self,
                 index = None, # Index class
                 title = None, # string : "ProductA"
                 tag = None, # string tuple : ("tagA", "tagB")
                 balstrt = 0, # int
                 note = "" # string
                 ):
        # index 입력
        if isinstance(index, Index):
            self.cindex = index
            self.index = index.index
        elif isinstance(index, PrjtIndex):
            self.cindex = index._prjt
            self.index = index.index
            
        # title 입력
        self.title = title
        
        # tag 입력 : tag는 튜플로 받음. string으로 입력된 경우 튜플로 변환 필요
        if isinstance(tag, tuple):
            self.tag = tag
        elif isinstance(tag, str):
            self.tag = tuple(tag)
        elif tag is None:
            self.tag = None
        else:
            raise ValueError("tag is not a tuple")
            
        # balstrt 입력
        self.balstrt = balstrt
        
        # note 입력
        self.note = note
        
        # Initialize
        self._intlz()

    def _intlz(self):
        # 초기화 함수 실행
        self._setdf()
        self._setjnl()
        self._set_outputfunc()
    
    #### INITIAL SETTING FUNCTION #### 초기화 함수
    DFCOL = ['add_scdd', 'add_scdd_cum', 'sub_scdd', 'sub_scdd_cum',
             'bal_strt', 'amt_add', 'amt_add_cum', 
             'amt_sub', 'amt_sub_cum', 'bal_end',
             'add_rsdl_cum', 'sub_rsdl_cum']
    DFCOL_smry = ['add_scdd', 'sub_scdd', 
                  'bal_strt', 'amt_add', 'amt_sub', 'bal_end']
    JNLCOL = ['amt_add', 'amt_sub', 'rcvfrom', 'payto', 'note']
    def _setdf(self):
        # DataFrame 초기화
        self._df = pd.DataFrame(np.zeros([len(self.index), len(self.DFCOL)]),
                               columns = self.DFCOL, 
                               index = self.index)
        self._df.loc[self.index[0], 'bal_strt'] = self.balstrt
        
        # balance 계산 실행
        self._cal_bal()
        
    def _setjnl(self):
        # Journal(분개장) 초기화
        self.jnl = pd.DataFrame(columns = self.JNLCOL)
    #### INITIAL SETTING FUNCTION ####
    
    #### DECORATOR ####
    def listwrapper(func):
        @wraps(func)
        def wrapped(self, *args):
            is_iter = True
            for arg in args:
                if is_iterable(arg) is False:
                    is_iter = False
            if is_iter is True:
                ilen = len(args[0])
                for i in range(ilen):
                    new_args = []
                    for val in args:
                        new_args = new_args + [val[i]]
                    new_args = tuple(new_args)
                    func(self, *new_args)
            else:
                new_args = args
                func(self, *new_args)
        return wrapped
                
    #### DECORATOR ####
     
    #### CALCULATE DATA BALANCE ####
    def _cal_bal(self):
        # 누적합 계산
        self._df.loc[:, 'add_scdd_cum'] = self._df.loc[:, 'add_scdd'].cumsum()
        self._df.loc[:, 'sub_scdd_cum'] = self._df.loc[:, 'sub_scdd'].cumsum()
        self._df.loc[:, 'amt_add_cum'] = self._df.loc[:, 'amt_add'].cumsum()
        self._df.loc[:, 'amt_sub_cum'] = self._df.loc[:, 'amt_sub'].cumsum()
        
        # 계좌 잔액 계산
        for i, idx in enumerate(self.index):
            if i > 0:
                self._df.loc[idx, 'bal_strt'] = self._df.loc[self.index[i-1], 'bal_end']
            self._df.loc[idx, 'bal_end'] = self._df.loc[idx, 'bal_strt'] \
                                          + self._df.loc[idx, 'amt_add'] \
                                          - self._df.loc[idx, 'amt_sub']
        
        # 누적 합 차액 계산
        self._df.loc[:, 'add_rsdl_cum'] = self._df.loc[:, 'add_scdd_cum'] \
                                         - self._df.loc[:, 'amt_add_cum']
        self._df.loc[:, 'sub_rsdl_cum'] = self._df.loc[:, 'sub_scdd_cum'] \
                                         - self._df.loc[:, 'amt_sub_cum']
    #### CALCULATE DATA BALANCE ####
        
    
    #### INPUT DATA ####
    @listwrapper
    def addscdd(self, index, amt):
        self._df.loc[index, 'add_scdd'] += amt
        self._cal_bal()

    @listwrapper
    def subscdd(self, index, amt):
        self._df.loc[index, 'sub_scdd'] += amt
        self._cal_bal()
        
    @listwrapper
    def addamt(self, index, amt, rcvfrom=None, note="add_amt"):
        if amt == 0:
            return
            
        # 분개장(journal)에 데이터 입력
        self.iptjnl(index, amt, 0, rcvfrom, None, note)
        
        # DataFrame에 데이터 입력
        self._df.loc[index, 'amt_add'] += amt
        
        # Balance 계산 실행
        self._cal_bal()
        
    @listwrapper
    def subamt(self, index, amt, payto=None, note="sub_amt"):
        if amt == 0:
            return
            
        # 분개장(journal)에 데이터 입력
        self.iptjnl(index, 0, amt, None, payto, note)
        
        # DataFrame에 데이터 입력
        self._df.loc[index, "amt_sub"] += amt
        
        # Balance 계산 실행
        self._cal_bal()
        
    @listwrapper
    def iptamt(self, index, amt, rcvfrom=None, payto=None, note=None):
        if amt == 0:
            return
        
        # amt가 양수인 경우 addamt 실행, 음수인 경우 subamt 실행
        if amt > 0:
            self.addamt(index, amt, rcvfrom, note)
        else:
            self.subamt(index, -amt, payto, note)
    
    def iptjnl(self, index, addamt, subamt, rcvfrom=None, payto=None, note=None):
        tmpjnl = pd.DataFrame([[addamt, subamt, rcvfrom, payto, note]], \
                              columns=self.JNLCOL, index=[index])
        self.jnl = pd.concat([self.jnl, tmpjnl])
    
    #### INPUT DATA ####


    #### OUTPUT DATA ####
    
    def _set_outputfunc(self):
        """
        Column명을 기준으로 데이터프레임에서 요구되는 값을 찾아서 반환
        """
        self.add_scdd = self.add_scdd(self)
        self.add_scdd_cum = self.add_scdd_cum(self)
        self.sub_scdd = self.sub_scdd(self)
        self.sub_scdd_cum = self.sub_scdd_cum(self)
        self.bal_strt = self.bal_strt(self)
        self.amt_add = self.amt_add(self)
        self.amt_add_cum = self.amt_add_cum(self)
        self.amt_sub = self.amt_sub(self)
        self.amt_sub_cum = self.amt_sub_cum(self)
        self.bal_end = self.bal_end(self)
        self.add_rsdl_cum = self.add_rsdl_cum(self)
        self.sub_rsdl_cum = self.sub_rsdl_cum(self)    
    
    class getattr_dfcol:
        """
        데코레이터
        클래스명을 column 이름으로 받아서 dataframe에서 index no, column name으로
        값을 찾아서 반환함.
        """
        def __call__(self, cls):
            def init(self, sprinstnc):
                self.sprinstnc = sprinstnc # super instance <- 상위 클래스의 인스턴스를 의미
                self.colname = cls.__name__
            cls.__init__ = init
            
            def getitem(self, idxno):
                return self.sprinstnc._df.loc[idxno, self.colname]
            cls.__getitem__ = getitem
            
            return cls
    
    @getattr_dfcol()
    class add_scdd:
        pass
    @getattr_dfcol()
    class add_scdd_cum:
        pass
    @getattr_dfcol()
    class sub_scdd:
        pass
    @getattr_dfcol()
    class sub_scdd_cum:
        pass
    @getattr_dfcol()
    class bal_strt:
        pass
    @getattr_dfcol()
    class amt_add:
        pass
    @getattr_dfcol()
    class amt_add_cum:
        pass
    @getattr_dfcol()
    class amt_sub:
        pass
    @getattr_dfcol()
    class amt_sub_cum:
        pass
    @getattr_dfcol()
    class bal_end:
        pass
    @getattr_dfcol()
    class add_rsdl_cum:
        pass
    @getattr_dfcol()
    class sub_rsdl_cum:
        pass
        
    
    # 일반적인 데이터 출력 함수
    @property
    def df(self):
        return self._df.loc[:, self.DFCOL_smry]

    
    def __getattr__(self, attr):
        """
        기존에 정의되어 있지 않은 속성이 입력될 경우, 객체를 조회하여 속성을 반환
        """ 
        return self.__dict__[attr]
        
        
    # Calculate the amount required in excess of the balance.
    def amt_rqrd_excess(self, idxno, rqrdamt, minunit = 100):
        """총 필요한 금액(rqrdamt)에 대하여 계좌 잔액을 초과하는 금액"""
        amt_rqrd = max(rqrdamt - self.bal_end[idxno], 0)
        amt_rqrd = round_up(amt_rqrd, -log10(minunit))
        return amt_rqrd
    
    #### OUTPUT DATA ####


    #### ACCOUNT TRANSFER ####
    def send(self, index, amt, account, note=None):
        # 본 account에서 입력된 account로 계좌 이체
        self.subamt(index, amt, account.title, note)
        account.addamt(index, amt, self.title, note)
    #### ACCOUNT TRANSFER ####


class Merge(object):
    """
    PARAMETERS
    - dct : Account dictionary. ex) {"nameA":A, "nameB":B, ...}
    ATTRIBUTES
    - df : Dataframe of data summary
    - _df : Dataframe of all data
    - add_scdd : get value of "add_scdd" column
      ex) Account.add_scdd[idx[0]]
    - add_scdd_cum : get value of "add_scdd_cum" column
    - sub_scdd : get value of "sub_scdd" column
    - sub_scdd_cum : get value of "sub_scdd_cum" column
    - bal_strt : get value of "bal_strt" column
    - amt_add : get value of "amt_add" column
    - amt_add_cum : get value of "amt_add_cum" column
    - amt_sub : get value of "amt_sub" column
    - amt_sub_cum : get value of "amt_sub_cum" column
    - bal_end : get value of "bal_end" column
    - add_rsdl_cum : get value of "add_rsdl_cum" column
    - sub_rsdl_cum : get value of "sub_rsdl_cum" column
    METHODS
    - dfcol(col, col_criteria=False) : Return a dataframe sorted by column name.
      + col : str(col name) or list of str(col name)
    - title() : Gather title data on each instances of dictionary
    - tag() : Gather tag data on each instances of dictionary
    - note() : Gather note data on each instances of dictionary 
    """
    def __init__(self, dct:dict):
        self.dct = dct
        self._set_idxmain()
        self._set_outputfunc()
    
    def __getitem__(self, dct_key):
        return self.dct[dct_key]
    
    @property
    def _df(self):
        # merge 완료된 dataframe 출력
        tmp_dct = sum([self._adjust_idx(self.dct[x]._df) for x in self.dct])
        return tmp_dct
        
    @property
    def df(self):
        # merge 완료된 dataframe을 요약하여 출력
        tmp_dct = sum([self._adjust_idx(self.dct[x].df) for x in self.dct])
        return tmp_dct
    
    def dfcol(self, col, col_criteria=False):
        # column명 구분에 따라 dictionary 데이터를 취합
        if isinstance(col, str):
            tmp_dct = pd.DataFrame({x: self.dct[x]._df.loc[:, col] 
                                   for x in self.dct})
        elif isinstance(col, list):
            col_lst = col
            if col_criteria:
                tmp_dct = pd.DataFrame({(col, x): self.dct[x]._df.loc[:, col] 
                                       for col in col_lst
                                       for x in self.dct})
            else:
                tmp_dct = pd.DataFrame({(x, col): self.dct[x]._df.loc[:, col] 
                                       for x in self.dct
                                       for col in col_lst})
        tmp_dct.fillna(0, inplace=True)
        return tmp_dct
    
    ##################################
    #### OUTPUT DATA ####
    
    def _set_outputfunc(self):
        """
        Column명을 기준으로 데이터프레임에서 요구되는 값을 찾아서 반환
        """
        self.add_scdd = self.add_scdd(self)
        self.add_scdd_cum = self.add_scdd_cum(self)
        self.sub_scdd = self.sub_scdd(self)
        self.sub_scdd_cum = self.sub_scdd_cum(self)
        self.bal_strt = self.bal_strt(self)
        self.amt_add = self.amt_add(self)
        self.amt_add_cum = self.amt_add_cum(self)
        self.amt_sub = self.amt_sub(self)
        self.amt_sub_cum = self.amt_sub_cum(self)
        self.bal_end = self.bal_end(self)
        self.add_rsdl_cum = self.add_rsdl_cum(self)
        self.sub_rsdl_cum = self.sub_rsdl_cum(self)    
    
    class getattr_dfcol:
        """
        데코레이터
        클래스명을 column 이름으로 받아서 dataframe에서 index no, column name으로
        값을 찾아서 반환함.
        """
        def __call__(self, cls):
            def init(self, sprinstnc):
                self.sprinstnc = sprinstnc # super instance <- 상위 클래스의 인스턴스를 의미
                self.colname = cls.__name__
            cls.__init__ = init
            
            def getitem(self, idxno):
                return self.sprinstnc._df.loc[idxno, self.colname]
            cls.__getitem__ = getitem
            
            return cls
    
    @getattr_dfcol()
    class add_scdd:
        pass
    @getattr_dfcol()
    class add_scdd_cum:
        pass
    @getattr_dfcol()
    class sub_scdd:
        pass
    @getattr_dfcol()
    class sub_scdd_cum:
        pass
    @getattr_dfcol()
    class bal_strt:
        pass
    @getattr_dfcol()
    class amt_add:
        pass
    @getattr_dfcol()
    class amt_add_cum:
        pass
    @getattr_dfcol()
    class amt_sub:
        pass
    @getattr_dfcol()
    class amt_sub_cum:
        pass
    @getattr_dfcol()
    class bal_end:
        pass
    @getattr_dfcol()
    class add_rsdl_cum:
        pass
    @getattr_dfcol()
    class sub_rsdl_cum:
        pass
        
    #### OUTPUT DATA ####
    ##################################
    
    
    def title(self):
        # dictionary 데이터 상 title 값 취합
        tmp_dct = pd.Series({x: self.dct[x].title for x in self.dct})
        return tmp_dct
    
    def tag(self):
        # dictionary 데이터 상 tag 값 취합
        tmp_dct = pd.Series({x: self.dct[x].tag for x in self.dct})
        return tmp_dct
    
    def note(self):
        # dictionary 데이터 상 note 값 취합
        tmp_dct = pd.Series({x: self.dct[x].note for x in self.dct})
        return tmp_dct

    def __getattr__(self, attr):
        """
        기존에 정의되어 있지 않은 속성이 입력될 경우, Account 객체를 조회하여 속성
        존재 여부를 확인함.
        """
        return [dctval.__dict__[attr] for dctval in self.dct.values()]
    
    #### 작성 중 ####
    # 기준 index 설정
    def _set_idxmain(self):
        idx_len = 0
        self.idx_main = None
        for x in self.dct:
            tmpidx = self.dct[x].df.index
            if len(tmpidx) > idx_len:
                idx_len = len(tmpidx)
                self.idx_main = tmpidx
    
    # index 조정
    def _adjust_idx(self, tmpdf):
        if len(tmpdf.index) < len(self.idx_main):
            return DataFrame(tmpdf, index=self.idx_main).fillna(0)
        return tmpdf
    #### 작성 중 ####
        

"""
class _idxsrch:
    def __init__(self) -> None:
        self._name = None
    
    def __set_name__(self, owner, name):
        self._name = name
        
    def __set__(self, instance, value):
        instance.__dict__[self._name] = value
"""     
        

class Intlz_accounts:
    def __init__(self,
                 index, # index
                 accname, # list
                 ):
        self.index = index
        self.accname = accname

        self.dct = {}
        self._intlz()
        
    def __len__(self):
        return len(self.accname)
        
    def _intlz(self):
        for no, accname in enumerate(self.accname):
            tmp_acc = Account(self.index, title=accname)
            self.dct[accname] = tmp_acc
            setattr(self, accname, tmp_acc)
            
        self.ttl = Merge(self.dct)
        for no, accname in enumerate(self.accname):
            setattr(self.ttl, accname, getattr(self, accname))
                 
                 
                 
                 
                 
     