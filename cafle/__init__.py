#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong

CAFLE
-----
"cafle" is a package that can be used to estimate the cash flow of financial investments. "Account" and "Loan" modules on "cafle" make it easier to estimate the cash flow of the financial investments.

Financial planners and investors in charge of investment projects often estimate the cash flow of investment projects to review the adequacy of investment. This package can be used where various financial models are needed, from large projects such as some real estate development projects, and infrastructure development projects to individual financial plans.

In many cases, it takes more than a few weeks to create a financial model with Excel, but it also takes a considerable amount of time to modify or create a new model according to investment requirements. If the size of the model increases above a certain level, it is not easy to interpret or modify it.

"cafle" will greatly reduce the time spent using Excel.
"""

from .genfunc import *
from .index import *
from .account import *
from .loan import *
from .write import *
from .assumption import *
