#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021.12.24
Golf club developing project

@author: KP_Hong
"""

import cafle as cf

class Intlz(object):
    def __init__(self, cidx):
        setattr(self, 'amtrnt', 1_000)
        cf.set_scd(self, 'acc', '임차료', cidx, 'subscd',
            scdidx = cidx.fund,
            scdamt = [self.amtrnt for _ in cidx.fund])
    
    
    
    