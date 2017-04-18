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
from datetime import timedelta,date,datetime
from multiprocessing.dummy import Pool as ThreadPool
import socket
import json
import tushare as ts
socket.setdefaulttimeout(10.0)
import config.Globaldata as conf


#first get the all stock list
#then get each stock today's info
#get the index today info
#compare every stock if the increase equal or bigger than index


#mylist = ['SZ002573','SZ300182','SZ300498','SH600816','SZ000001','SZ002603','SZ002074','SZ000895','SZ002405','SZ300244','SZ000538','SZ300072','SZ300352','SZ000860','SH600197','SH600612','SH600988','SZ002236','SZ002716','SH601788','SZ002242','SZ002706','SZ300124','SH600599','SH601601','SZ002415','SZ001979','SZ399905','SZ300449','SZ300368','SZ399006','SZ002095','SZ000651','SZ300458','SH600648','SZ002292','SZ002130','SZ300369','SH600570','SZ300088','SZ088551','SZ002268','SZ300033','SZ000629','SZ002145','SH601519','SH600660','SH600036','SH601939','SH600547','SZ088115','SH601198','SZ002460','SZ002594','SH600436','SH600745','SZ000415','SZ300401','SH600511','SZ002151','SH600149','SH600383','SH600606','SH600078','SZ300262']
#myStlist = ['002573','300182','300498','600816','000001','002603','002074','000895','002405','300244','000538','300072','300352','000860','600197','600612','600988','002236','002716','601788','002242','002706','300124','600599','601601','002415','001979','399905','300449','300368','399006','002095','000651','300458','600648','002292','002130','300369','600570','300088','088551','002268','300033','000629','002145','601519','600660','600036','601939','600547','088115','601198','002460','002594','600436','600745','000415','300401','600511','002151','600149','600383','600606','600078','300262']

#this func for thread
def threadCalc(stockCode):
	#print "download stock history data:",stockCode
	crawlHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
	url = "http://xueqiu.com/S/"+stockCode.upper()+"/historical.csv"
	#url = "http://table.finance.yahoo.com/table.csv?s="+stockCode
	print "download stock: ",stockCode
	repeated = 1
	while repeated:
		try:
			cookie = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
			urllib2.install_opener(opener)
			req = urllib2.Request(url,None,crawlHeader)
			req.add_header("Accept","*/*")
			req.add_header("Accept-Language", "*")
			req.add_header("Connection", "keep-alive")
			req.add_header("Accept-Encoding", "none")
			req.add_header("X-Requested-With", "XMLHttpRequest")
			req.add_header("Referer", "http://baidu.com")
			req.add_header("Cache-Control","no-cache")
			req.add_header("X-Requested-With","XMLHttpRequest")
			req.add_header("Host","xueqiu.com")
			resp = urllib2.urlopen(req)
			#print resp.getcode()
			d = resp.read()
			f = open(stockCode+'temp.csv','w')
			f.write(d)
			f.close()
			#req.close()

			#urllib.urlretrieve(url,stockCode+'temp.csv')
			repeated = 0
		except Exception, e:
			print "meet exception, will download again after 5 seconds:",stockCode , str(e)
			time.sleep(5)
	#remove the price=0 line
	time.sleep(2)
	filename = conf.tushare_download + '/'+'%s.csv'%stockCode
	f = open(stockCode+'temp.csv','r')
	nf = open(filename,'w')
	for line in f.readlines():
		arr = line.split(',')
		if arr[2]=='\"0.0\"':
			pass
		else:
			nf.write(line)
	nf.close()
	f.close()
	os.remove(stockCode+'temp.csv')
	calcAllInstructor(stockCode)
	print "rebuild ewma index finish :",stockCode




#too slow, change to thread download method
def appendDownloadByMultiThread(stockCode):
    tday = time.strftime('%Y-%m-%d',time.localtime())

    print(stockCode)
    repeated = 1
    while repeated:
        #try:
        filename = conf.tushare_download + '/'+'%s.csv'%stockCode
        if os.path.exists(filename):
            stockData = pandas.read_csv(filename)
            co = stockData['close'].count()
            lastDay = stockData['date'][co - 1]
            print "update from " + lastDay

            #todo 停牌，周末等非交易日会重复写
            if lastDay == tday:
                #stockData.close()
                repeated = 0
                return;
            else:
                writeMode = 'a'
                withHeader = False
                lastDay = datetime.strptime(lastDay, '%Y-%m-%d')
                lastDay = lastDay + timedelta(days=1)
                lastDay = datetime.strftime(lastDay,'%Y-%m-%d')
                print lastDay
        else:
            writeMode = 'w'
            withHeader = True
            lastDay = '2005-01-01'
            print lastDay
            #_data_.to_csv(filename,encoding='gbk')

        #find the last updated day.
        #tempData = ts.get_hist_data(str(code),start=lastDay,end=tday)
        tempData = ts.get_k_data(str(stockCode),start=lastDay,end=tday)
        repeated = 0
        #except Exception, e:
        #    print "meet exception, will download again after 5 seconds:",stockCode , str(e)
        #    time.sleep(50)

    #按爬虫版本的格式调整，并追加 1 截取date    open    high     low   close     volume 2 增加"symbol"le
    wrData = tempData.ix[:,['code','date','open','high','low','close','volume']]
    #wrData.sort_index(inplace = True)
    #wrData.reset_index(level=0, inplace=True)

    #wrData.insert(0,'symbol',stockCode)
    #tmp=wrData.set_index('symbol')

    if wrData is not None and wrData.size != 0:
        wrData.to_csv(filename, mode=writeMode, header=withHeader,encoding='gbk')
        #wrData.close()
        print "append list down finish"
        calcAllInstructor(stockCode)
        print "rebuild ewma index finish :",stockCode

#TODO append function is tobe completed.
def appendDownload():
    #read stock lists.
    dat = ts.get_industry_classified()
    tday = time.strftime('%Y-%m-%d',time.localtime())
    i=0
    for code in dat['code'].values:
        i+= 1
        print(i,code)
        try:
            if code >= u'600000':
                stockCode = 'SH'+ str(code)
            else:
                stockCode = 'SZ'+ str(code)
            filename = conf.tushare_download + '/'+ '%s.csv'%stockCode

            if os.path.exists(filename):
                stockData = pandas.read_csv(filename)
                co = stockData['close'].count()
                lastDay = stockData['date'][co - 1]
                #todo 停牌，周末等非交易日会重复写
                if lastDay == tday:
                    continue;
                else:
                    writeMode = 'a'
                    withHeader = False
            else:
                writeMode = 'w'
                withHeader = True
                lastDay = '2000-08-01'
                #_data_.to_csv(filename,encoding='gbk')

            #find the last updated day.
            tempData = ts.get_k_data(str(code),start=lastDay,end=tday)

            #df2=pd.DataFrame({'symbol':pd.Series('SH600606',index=list(range(len(yy)))),})

            #按爬虫版本的格式调整，并追加 1 截取date    open    high     low   close     volume 2 增加"symbol"le
            #wrData = tempData.ix[:,['open','high','low','close','volume']]
            #wrData.sort_index(inplace = True)
            #wrData.reset_index(level=0, inplace=True)
            #yy.insert(0,'symbol','sh')
            wrData = tempData.ix[:,['date','open','high','low','close','volume']]

            wrData.insert(0,'symbol',stockCode)
            tmp=wrData.set_index('symbol')

            if tmp is not None and tmp.size != 0:
                tmp.to_csv(filename, mode=writeMode, header=withHeader,encoding='gbk')
                print "append list down finish"
                calcAllInstructor(stockCode)
                print "rebuild ewma index finish :",stockCode
        except IOError:
            pass    #不行的话还是continue
    #print len(inuse)


def getnewstlist():
    stslists = []
    dat = ts.get_industry_classified()
    yy = list(dat['code'])
     #ttt=['sh'+i for i in yy]
    for x in yy:
        if x >= u'600000':
            stslists.append('SH'+x)
         #elif x.startwith('3'):
        else:
            stslists.append('SZ'+x)
		#stslists.append(x['stcode'])
    return stslists

def threadUpdate():
	#down csv from tushare
	newlists = getnewstlist()
	pool = ThreadPool(12)
	results = pool.map(appendDownloadByMultiThread,newlists)
	pool.close()
	pool.join()
	print "update all stock finish!"


def mylistDownload():
    for code in conf.myStlist:
        appendDownloadByMultiThread(code)
	#pool = ThreadPool(1)
	#results = pool.map(appendDownloadByMultiThread, myStlist)
	#pool.close()
	#pool.join()
	print "my list down finish"

def threadDownload():
    for fi in os.listdir(os.getcwd()):
        if fi.find(conf.tushare_download + '/'+'.csv')>-1:
            os.remove(fi)

	#down csv from xueqiu
	newlists = getnewstlist()
	pool = ThreadPool(12)
	results = pool.map(threadCalc,newlists)
	pool.close()
	pool.join()
	print "download all stock finish!"



def calcAllInstructor(stockCode):
	#MACD params is 5,10,7
	filename = conf.tushare_download + '/'+'%s.csv'%stockCode
	stock_data = pandas.read_csv(filename)
	if stock_data['close'].count()==0:
		print stockCode," has no stock data, maybe exist stock market"
		return

	stock_data['amplitude'] = numpy.round(stock_data['close'].diff(),3)
	stock_data['percent'] = numpy.round(stock_data['close'].pct_change(),4)
	stock_data['MA3'] = numpy.round(pandas.rolling_mean(stock_data['close'],3),3)
	stock_data['EMA5'] = numpy.round(pandas.ewma(stock_data['close'],span=5),3)
	stock_data['EMA10'] = numpy.round(pandas.ewma(stock_data['close'],span=10),3)
	stock_data['EMA14'] = numpy.round(pandas.ewma(stock_data['close'],span=14),3)
	stock_data['EMA20'] = numpy.round(pandas.ewma(stock_data['close'],span=20),3)
	stock_data['EMA30'] = numpy.round(pandas.ewma(stock_data['close'],span=30),3)
	stock_data['EMA22'] = numpy.round(pandas.ewma(stock_data['close'],span=22),3)
	stock_data['EMA250'] = numpy.round(pandas.ewma(stock_data['close'],span=250),3)
	stock_data['EMA888'] = numpy.round(pandas.ewma(stock_data['close'],span=888),3)
	stock_data['DIFF'] = map(lambda x,y:x-y, stock_data['EMA10'],stock_data['EMA22'])
	stock_data['DEA'] = numpy.round(pandas.rolling_mean(stock_data['DIFF'],7),3)

	stock_data['abspercent'] = map(lambda x:x*100 ,stock_data['percent'])
	stock_data['EMA15PER'] = numpy.round(pandas.ewma(stock_data['abspercent'],span=15),3)

	stock_data['EMA5LOW'] = numpy.round(pandas.ewma(stock_data['low'],span=5),3)
	stock_data['EMA10LOW'] = numpy.round(pandas.ewma(stock_data['low'],span=10),3)
	stock_data['EMA15LOW'] = numpy.round(pandas.ewma(stock_data['low'],span=15),3)
	stock_data['EMA20LOW'] = numpy.round(pandas.ewma(stock_data['low'],span=20),3)

	#now KDJ params is 9,3,3
	stock_data['low9'] = pandas.rolling_min(stock_data['close'],9)
	stock_data['high9'] = pandas.rolling_max(stock_data['close'],9)
	stock_data['quick_k'] = map(lambda x,y,z:numpy.round((x-y)/(z-y)*100,2) if z>y else 0, stock_data['close'],stock_data['low9'],stock_data['high9'])
	stock_data['quick_d'] = numpy.round(pandas.rolling_mean(stock_data['quick_k'],3),2)
	stock_data['slow_d'] = numpy.round(pandas.rolling_mean(stock_data['quick_d'],3),2)

	#calc low open diff
	stock_data['lowopendiff'] = map(lambda x,y:(x-y)*200/(x+y),stock_data['high'],stock_data['low'])
	stock_data['lowdiffmacd'] = numpy.round(pandas.ewma(stock_data['lowopendiff'],span=9),3)
	stock_data['lowclosediff'] = map(lambda x,y:x-y,stock_data['close'],stock_data['low'])
	stock_data['lowdiffmacd2'] = numpy.round(pandas.ewma(stock_data['lowclosediff'],span=14),3)

	stock_data['maxclosediff'] = map(lambda x: x if x>0 else 0, stock_data['amplitude'])
	stock_data['absclosediff'] = map(lambda x: x if x>0 else -x, stock_data['amplitude'])
	stock_data['fmrsi'] = numpy.round(pandas.ewma(stock_data['maxclosediff'],span=5),3)
	stock_data['fzrsi'] = numpy.round(pandas.ewma(stock_data['absclosediff'],span=5),3)
	stock_data['rsi5'] = numpy.round(map(lambda x,y: x/y*100, stock_data['fmrsi'],stock_data['fzrsi']),2)


	stock_data['highlowdiff'] = map(lambda x,y: x-y, stock_data['high'],stock_data['low'])
	stock_data['highlowdiffema5'] = numpy.round(pandas.ewma(stock_data['highlowdiff'],span=5),3)

	stock_data['bollstd'] = numpy.round(pandas.rolling_std(stock_data['close'],14),3)

	stock_data['jd'] = map(lambda x,y:x*y, stock_data['amplitude'],stock_data['volume'])
	stock_data['ejd'] = pandas.ewma(stock_data['jd'],span=3)

	stock_data['newdiverse10']=numpy.round(map(lambda x,y:x/y-1,stock_data['close'],stock_data['EMA10']),4)

	#stock_data['lowvolume89'] = pandas.rolling_min(stock_data['volume'],89)
	#stock_data['lowvolume144'] = pandas.rolling_min(stock_data['volume'],144)
	#stock_data['highvolume89'] = pandas.rolling_max(stock_data['volume'],89)
	#stock_data['highvolume144'] = pandas.rolling_max(stock_data['volume'],144)

	stock_data.to_csv(conf.tushare_download + '/'+ stockCode+'_ewma.csv')


def testFunction():
    print 'for function test'

def SelectFunction(input_key):
    function_map = {
                     'd':threadDownload,
                     'u':appendDownload,
                     't':threadUpdate,
                     'm':mylistDownload,
                     'c':testFunction,
                    }
    return function_map[input_key]()
    #c = input("Please Enter a Char:")
    #if c == 'd':
    #    threadDownload()
    #elif c == 'u':
    #    #appendDownload()
    #    print 'uuu'

def downloadDailyStockData():
    print "remove old data files....."

    print "d: delete csv first then thread download stock history data."
    print "u: Updated all stock history data."
    print "m: download My selected stock history data."

    c = raw_input("Please Enter a Char:")
    print "start download: ",time.strftime('%Y-%m-%d %X',time.localtime())
    #SelectFunction(c)
    if 'm' == c:
        mylistDownload()
    elif 't' == c:
        threadUpdate()  #update download all with multi thread
    elif 'u' == c:
        appendDownload()  #update download all

    print "finish download: ",time.strftime('%Y-%m-%d %X',time.localtime())


if __name__ == '__main__':
    downloadDailyStockData()