#!/usr/bin/env python
# ---------------------------------------------------------------------------- #
# Developer: Andrew Kirfman & Cuong Do                                         #
# Project: CSCE-470 Project Task #3                                            #
#                                                                              #
# File: ./bollinger_bands.py                                                   #
# ---------------------------------------------------------------------------- #


import os, re, sys, time, datetime, copy, shutil

sys.path.append("./yahoo_finance_data_extract")

import pandas
from yahoo_finance_historical_data_extract import YFHistDataExtr
import matplotlib.pyplot as plt
 
def calculate_bands(ticker_symbol):
    # Delete the old bands image for this picture
    os.system("rm ./static/pictures/%s.png" % ticker_symbol)

    data_ext = YFHistDataExtr()
    data_ext.set_interval_to_retrieve(400)#in days
    data_ext.set_multiple_stock_list([str(ticker_symbol)])
    data_ext.get_hist_data_of_all_target_stocks()
    # convert the date column to date object
    data_ext.all_stock_df['Date'] =  pandas.to_datetime( data_ext.all_stock_df['Date'])
    temp_data_set = data_ext.all_stock_df.sort('Date',ascending = True ) #sort to calculate the rolling mean
    
    temp_data_set['20d_ma'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=5)
    temp_data_set['50d_ma'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=50)
    temp_data_set['Bol_upper'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=80) + 2* pandas.rolling_std(temp_data_set['Adj Close'], 80, min_periods=80)
    temp_data_set['Bol_lower'] = pandas.rolling_mean(temp_data_set['Adj Close'], window=80) - 2* pandas.rolling_std(temp_data_set['Adj Close'], 80, min_periods=80)
    temp_data_set['Bol_BW'] = ((temp_data_set['Bol_upper'] - temp_data_set['Bol_lower'])/temp_data_set['20d_ma'])*100
    temp_data_set['Bol_BW_200MA'] = pandas.rolling_mean(temp_data_set['Bol_BW'], window=50)#cant get the 200 daa
    temp_data_set['Bol_BW_200MA'] = temp_data_set['Bol_BW_200MA'].fillna(method='backfill')##?? ,may not be good
    temp_data_set['20d_exma'] = pandas.ewma(temp_data_set['Adj Close'], span=20)
    temp_data_set['50d_exma'] = pandas.ewma(temp_data_set['Adj Close'], span=50)
    data_ext.all_stock_df = temp_data_set.sort('Date',ascending = False ) #revese back to original
     
    data_ext.all_stock_df.plot(x='Date', y=['Adj Close','20d_ma','50d_ma','Bol_upper','Bol_lower' ])
    #data_ext.all_stock_df.plot(x='Date', y=['Bol_BW','Bol_BW_200MA' ])
    
    plt.savefig('./static/pictures/%s.png' % ticker_symbol)
    return temp_data_set['Adj Close'], temp_data_set['Bol_lower'], temp_data_set['20d_ma']
    #plt.show()
