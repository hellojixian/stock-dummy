#!/usr/bin/env python3

import pandas as pd
import numpy as np

class Strategy(object):
    def __init__(self, init_settings=None):
        self.position = 'empty'
        return

    def handle_data(feature):
        if self.position != 'empty':
            if self.should_hold(feature):
                return "hold"
            if self.should_sell(feature):
                self.position ='empty'
                return "sell"
        elif self.should_buy(feature):
            self.position ='full'
            return 'buy'
        else:
            return ''

    def should_buy(feature):
        return

    def should_sell(feature):
        return

    def should_hold(feature):
        return
