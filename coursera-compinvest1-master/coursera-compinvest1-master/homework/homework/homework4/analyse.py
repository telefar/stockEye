'''
(c) 2013 Remy Marquis
Computational Investing @ Georgia Tech
Homework 3

Create a portfolio analysis tool, analyze.py, that takes a command line like this:
python analyze.py values.csv \$SPX
'''

import pandas as pd
import pandas.io.parsers as pd_par
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

NUM_TRADING_DAYS = 252
ls_symbols = ["$SPX"]
valueFile = "values_h4-Q2.csv"

value_data = pd_par.read_csv(valueFile, header=None)
portVal = value_data[3].values.copy()

portVal = portVal / portVal[0]
dailyVal = portVal.copy()
tsu.returnize0(dailyVal)

daily_ret = np.mean(dailyVal)
vol = np.std(dailyVal)
sharpe = np.sqrt(NUM_TRADING_DAYS) * daily_ret / vol
cum_ret = portVal[len(portVal) -1]/portVal[0]

print "=== FUND ==="
print "Sharpe Ratio: ", sharpe
print "Volatility (stdev): ", vol
print "Average Daily Return: ", daily_ret
print "Cumulative Return: ", cum_ret

# Getting the start and end dates from the .csv file
df_lastrow = len(value_data) - 1
dt_start = dt.datetime( value_data.get_value(0, 0), value_data.get_value(0, 1), value_data.get_value(0, 2))
dt_end = dt.datetime( value_data.get_value(df_lastrow, 0), value_data.get_value(df_lastrow, 1), value_data.get_value(df_lastrow, 2) + 1 )

# Getting market data
dataobj = da.DataAccess('Yahoo')
ls_keys = ['close', 'actual_close']
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

temp = d_data['close'].values.copy()
portVal = temp / temp[0,:]

dailyVal = portVal.copy()
tsu.returnize0(dailyVal)

# Calculate statistics
daily_ret = np.mean(dailyVal)
vol = np.std(dailyVal)
sharpe = np.sqrt(NUM_TRADING_DAYS) * daily_ret / vol
cum_ret = portVal[len(portVal) -1]/portVal[0]

print "=== $SPX ==="
print "Sharpe Ratio: ", sharpe
print "Volatility (stdev): ", vol
print "Average Daily Return: ", daily_ret
print "Cumulative Return: ", cum_ret
