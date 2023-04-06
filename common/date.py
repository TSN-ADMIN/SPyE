#!/usr/bin/python

from datetime import datetime as dtm
import time

# default internal timestamp format
TIM_FMT = '%Y-%m-%d %H:%M:%S'


def now_():
    return int(round(time.time() * 1000))  # milliseconds


def tim_str(timestamp):
    return dtm.fromtimestamp(timestamp).strftime(TIM_FMT)
