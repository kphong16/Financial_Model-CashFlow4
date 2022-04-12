import os
from collections import namedtuple
import pandas as pd
from pandas import Series, DataFrame
import numpy as np

import cafle as cf
from cafle import (
    Account,
    Assumption_Base,
    Write,
    WriteWS,
    Cell,
)
from cafle.genfunc import (
    rounding as R,
    PY,
    Area,
    EmptyClass,
)
from cafle.assumption import read_standard_process_rate_table


#### Read Land Data ####
class LandMtrx(Assumption_Base):
    def __init__(self):
        super().__init__()

        DIRECTORY   = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        filename    = "/data/land.csv"
        fileloc     = DIRECTORY + filename

        self.rawdata = pd.read_csv(fileloc)
        self.rawdata['area_py'] = self.rawdata.area.apply(lambda x: Area(m2=x).py)

        self.ttl_area = sum(self.rawdata.area)
        self.ttl_areapy = sum(self.rawdata.area_py)
        self.ttl_value = sum(self.rawdata.value)

area = LandMtrx()


