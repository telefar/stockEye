__author__ = 'phabio'
# -*- coding: UTF-8 -*-
# -*- coding: UTF-8 -*-
#coding = utf-8

import urllib,urllib2
import httplib
import shutil
import os
import linecache
import codecs
import cookielib
from HTMLParser import HTMLParser
import numpy
import pandas
import time

import tushare as ts


#too slow, change to thread download method
def testappendDownloadByMultiThread(stockCode):
    tday = time.strftime('%Y-%m-%d',time.localtime())

    print(stockCode)

    lastDay = '2000-01-01'
    print lastDay
    #tempData = ts.get_hist_data(str(code),start=lastDay,end=tday)
    tempData = ts.get_k_data(str(stockCode),start=lastDay,end=tday)
    print "why not here"
    print tempData

testappendDownloadByMultiThread("300244")
