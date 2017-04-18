# -*- coding: UTF-8 -*-
# coding = utf-8

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
from multiprocessing.dummy import Pool as ThreadPool
import socket
import math
socket.setdefaulttimeout(10.0)
import config.Globaldata as conf


#first get the all stock list

#then get each stock today's info

#get the index today info

#compare every stock if the increase equal or bigger than index

mylist = ['002573','300182','300498','600816','000001','002603','002074','000895','002405','300244','000538','300072','300352','000860','600197','600612','600988','002236','002716','601788','002242','002706','300124','600599','601601','002415','001979','399905','300449','300368','399006','002095','000651','300458','600648','002292','002130','300369','600570','300088','088551','002268','300033','000629','002145','601519','600660','600036','601939','600547','088115','601198','002460','002594','600436','600745','000415','300401','600511','002151','600149','600383','600606','600078','300262']
nowshlist = ['600816','600197','600612','600988','601788','600599','601601','600648','600570','601519','600660','600036','601939','600547','601198','600436','600745','600511','600149','600383','600606','600078']
nowszlist = ['002573','000001','002603','002074','000895','002405','000538','000860','002236','002716','002242','002706','002415','001979','002095','000651','002292','002130','088551','002268','000629','002145','088115','002460','002594','000415','002151']
nowcylist = ['300182','300498','300244','300072','300352','300124','399905','300449','300368','399006','300458','300369','300088','300033','300401','300262']

def addStockPrefix(stock):
	if stock >= u'600000':
		stslists = 'SH'+ stock
	else:
		stslists = 'SZ'+ stock
	return stslists


def analyseMylist():
	crawlHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
	shurl = "http://hq.sinajs.cn/list=s_sh000001"
	#  http://bdcjhq.hexun.com/quote?s2=002519.sz
	szurl = "http://hq.sinajs.cn/list=s_sz399001"
	cyurl = "http://hq.sinajs.cn/list=s_sz399006"

	req2 = urllib2.Request(shurl,None,crawlHeader)
	resp2 = urllib2.urlopen(req2)
	d2 = resp2.read()
	fidx = d2.find("\"")
	eidx = d2.find("\"",fidx+1)
	s = d2[fidx+1:eidx]
	arr = s.split(',')
	v1 = '<p>ShangHai stock increase rate:<br>'+str(arr[0])+'&nbsp;'+str(arr[1])+'&nbsp;'+str(arr[3])+'%</p>'
	#print arr[0],arr[3],"%"

	req3 = urllib2.Request(szurl,None,crawlHeader)
	resp3 = urllib2.urlopen(req3)
	d3 = resp3.read()
	fidx = d3.find("\"")
	eidx = d3.find("\"",fidx+1)
	s1 = d3[fidx+1:eidx]
	arr2 = s1.split(',')
	v2 = '<p>ShenZhen stock increase rate:<br>'+str(arr2[0])+'&nbsp;'+str(arr2[1])+'&nbsp;'+str(arr2[3])+'%</p>'

	req4 = urllib2.Request(cyurl,None,crawlHeader)
	resp4 = urllib2.urlopen(req4)
	d4 = resp4.read()
	fidx = d4.find("\"")
	eidx = d4.find("\"",fidx+1)
	s2 = d4[fidx+1:eidx]
	arr3 = s2.split(',')


	too = time.strftime('%Y-%m-%d',time.localtime())
	anafile = time.strftime('%Y%m%d',time.localtime())
	f = codecs.open('analyse'+anafile+'.html','w',encoding='gbk')

	f.write('<p>My stock list analysis.</p><table border=1>')


	coo = 0
	for x in mylist:
		print "analyse : ",x
		if os.path.exists(conf.tushare_download + '/'+x+'_ewma.csv')==False:
			print "no file"
			continue
		stock_data = pandas.read_csv(conf.tushare_download + '/'+x+'_ewma.csv')
		if stock_data['close'].count==0:
			print "no close data"
			continue
		co = stock_data['close'].count()
		tc = stock_data['close'][co-1]
		hi = stock_data['high'][co-1]
		mlo = stock_data['low'][co-1]
		dt = stock_data['date'][co-1]

		rate = stock_data['percent'][co-1]*100

		f.write('<tr>')

		xwithprefix = addStockPrefix(x)
		href = '<a target=_blank href="http://xueqiu.com/s/'+ xwithprefix +'">' + xwithprefix + '</a>'
		vs = '<td>'+ str(dt) + '</td><td> close: '+ str(tc) + '</td><td>high: '+ str(hi) + '</td><td>low: '+ str(mlo) + '</td><td>' +href+'</td><td>'

		if x >= u'600000':
			tmpArr3Value = arr[3]
		elif x >= u'300000':
			tmpArr3Value = arr3[3]
		else:
			tmpArr3Value = arr2[3]

		if (rate>float(tmpArr3Value)) and (rate>0):
			vs += '<font color=red>' +str(rate)+'%</font></td>'
		else:
			vs += str(rate)+'%</td>'
		av = getAmpli(x)
		upp = get30daysup(x)
		macd = calcMACD(x)
		cmacd = calcMACDback(x)
		kdj = calcKDJ(x)
		ckdj = calcKDJback(x)
		ci = chaoDi(x)
		cbl = chaoBaoLuo(x)
		rcbl = realChaoBaoLuo(x)
		rsi5 = getRsi(x)
		vs = vs +av + upp + macd + cmacd + kdj + ckdj + rsi5 + ci + cbl + rcbl
		f.write(vs.decode('gbk'))
		f.write('</tr>')
		coo +=1

	f.write('</table>')
	f.close()


def analyse():
	crawlHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'}
	shurl = "http://hq.sinajs.cn/list=s_sh000001"
	#  http://bdcjhq.hexun.com/quote?s2=002519.sz
	szurl = "http://hq.sinajs.cn/list=s_sz399001"
	cyurl = "http://hq.sinajs.cn/list=s_sz399006"

	req2 = urllib2.Request(shurl,None,crawlHeader)
	resp2 = urllib2.urlopen(req2)
	d2 = resp2.read()
	fidx = d2.find("\"")
	eidx = d2.find("\"",fidx+1)
	s = d2[fidx+1:eidx]
	arr = s.split(',')
	v1 = '<p>ShangHai stock increase rate:<br>'+str(arr[0])+'&nbsp;'+str(arr[1])+'&nbsp;'+str(arr[3])+'%</p>'
	#print arr[0],arr[3],"%"


	req3 = urllib2.Request(szurl,None,crawlHeader)
	resp3 = urllib2.urlopen(req3)
	d3 = resp3.read()
	fidx = d3.find("\"")
	eidx = d3.find("\"",fidx+1)
	s1 = d3[fidx+1:eidx]
	arr2 = s1.split(',')
	v2 = '<p>ShenZhen stock increase rate:<br>'+str(arr2[0])+'&nbsp;'+str(arr2[1])+'&nbsp;'+str(arr2[3])+'%</p>'

	req4 = urllib2.Request(cyurl,None,crawlHeader)
	resp4 = urllib2.urlopen(req4)
	d4 = resp4.read()
	fidx = d4.find("\"")
	eidx = d4.find("\"",fidx+1)
	s2 = d4[fidx+1:eidx]
	arr3 = s2.split(',')


	too = time.strftime('%Y-%m-%d',time.localtime())
	anafile = time.strftime('%Y%m%d',time.localtime())
	f = codecs.open('analyse'+anafile+'.html','w',encoding='gbk')

	f.write('<p>ShangHai</p><table border=1>')


	coo = 0
	for x in nowshlist:
		print "analyse : ",x
		#pa = os.getcwd()
		if os.path.exists(conf.tushare_download + '/'+x+'_ewma.csv')==False:
			print "no file"
			continue
		stock_data = pandas.read_csv(conf.tushare_download + '/'+x+'_ewma.csv')
		if stock_data['close'].count==0:
			print "no close data"
			continue
		co = stock_data['close'].count()
		tc = stock_data['close'][co-1]
		hi = stock_data['high'][co-1]
		mlo = stock_data['low'][co-1]
		dt = stock_data['date'][co-1]
         #休息日，不开工
		#if dt!=too:
		#	print "not for today."
		#	continue
		rate = stock_data['percent'][co-1]*100
		#if rate>arr[3]:
		f.write('<tr>')

		xwithprefix = addStockPrefix(x)
		href = '<a target=_blank href="http://xueqiu.com/s/'+ xwithprefix +'">' + xwithprefix + '</a>'
		vs = '<td>'+ str(dt) + '</td><td> close: '+ str(tc) + '</td><td>high: '+ str(hi) + '</td><td>low: '+ str(mlo) + '</td><td>' +href+'</td><td>'
		if (rate>float(arr[3])) and (rate>0):
			vs += '<font color=red>' +str(rate)+'%</font></td>'
		else:
			vs += str(rate)+'%</td>'
		av = getAmpli(x)
		upp = get30daysup(x)
		macd = calcMACD(x)
		cmacd = calcMACDback(x)
		kdj = calcKDJ(x)
		ckdj = calcKDJback(x)
		ci = chaoDi(x)
		cbl = chaoBaoLuo(x)
		rcbl = realChaoBaoLuo(x)
		rsi5 = getRsi(x)
		vs = vs +av + upp + macd + cmacd + kdj + ckdj + rsi5 + ci + cbl + rcbl
		f.write(vs.decode('gbk'))
		f.write('</tr>')
		coo +=1

	f.write('</table><p>ShenZhen</p><p></p><table border=1>')

	coo=0
	for x in nowszlist:
		print "analyse : ",x
		#pa = os.getcwd()
		if os.path.exists(conf.tushare_download + '/'+x+'_ewma.csv')==False:
			continue
		stock_data = pandas.read_csv(conf.tushare_download + '/'+x+'_ewma.csv')
		if stock_data['close'].count==0:
			continue
		co = stock_data['close'].count()
		tc = stock_data['close'][co-1]
		hi = stock_data['high'][co-1]
		mlo = stock_data['low'][co-1]
		dt = stock_data['date'][co-1]
		#if dt!=too:
		#	continue
		rate = stock_data['percent'][co-1]*100
		#if rate>arr2[3]:
		f.write('<tr>')
		xwithprefix = addStockPrefix(x)
		href = '<a target=_blank href="http://xueqiu.com/s/'+ xwithprefix +'">' + xwithprefix + '</a>'
		vs = '<td>'+ str(dt) + '</td><td> close: '+ str(tc) + '</td><td>high: '+ str(hi) + '</td><td>low: '+ str(mlo) + '</td><td>' +href+'</td><td>'
		#vs = '<td>'+ str(dt) + '</td><td>'+ str(tc) + '</td><td>' +href+'</td><td>'
		if (rate>float(arr2[3])) and (rate>0):
			vs += '<font color=red>'+str(rate)+'%<font></td>'
		else:
			vs += str(rate)+'%</td>'
		av = getAmpli(x)
		upp = get30daysup(x)
		macd = calcMACD(x)
		cmacd = calcMACDback(x)
		kdj = calcKDJ(x)
		ckdj = calcKDJback(x)
		ci = chaoDi(x)
		cbl = chaoBaoLuo(x)
		rcbl = realChaoBaoLuo(x)
		rsi5 = getRsi(x)
		vs = vs +av + upp + macd + cmacd + kdj + ckdj + rsi5 + ci + cbl + rcbl
		f.write(vs.decode('gbk'))
		f.write('</tr>')
		coo +=1


	f.write('</table>')
	f.write('<p>Chuang Ye Ban</p><p></p><table border=1>')

	coo=0
	for x in nowcylist:
		print "analyse : ",x
		pa = os.getcwd()
		if os.path.exists(conf.tushare_download + '/'+x+'_ewma.csv')==False:
			continue
		stock_data = pandas.read_csv(conf.tushare_download + '/'+x+'_ewma.csv')
		if stock_data['close'].count==0:
			continue
		co = stock_data['close'].count()
		tc = stock_data['close'][co-1]
		hi = stock_data['high'][co-1]
		mlo = stock_data['low'][co-1]
		dt = stock_data['date'][co-1]
		#if dt!=too:
		#	print "rest day."
		#	continue
		rate = stock_data['percent'][co-1]*100
		#if rate>arr2[3]:
		f.write('<tr>')

		xwithprefix = addStockPrefix(x)
		href = '<a target=_blank href="http://xueqiu.com/s/'+xwithprefix+'">' + xwithprefix + '</a>'
		vs = '<td>'+ str(dt) + '</td><td> close: '+ str(tc) + '</td><td>high: '+ str(hi) + '</td><td>low: '+ str(mlo) + '</td><td>' +href+'</td><td>'
		#vs = '<td>'+ str(dt) + '</td><td>'+ str(tc) + '</td><td>' +href+'</td><td>'
		if (rate>float(arr3[3])) and (rate>0):
			vs += '<font color=red>'+str(rate)+'%<font></td>'
		else:
			vs += str(rate)+'%</td>'
		av = getAmpli(x)
		upp = get30daysup(x)
		macd = calcMACD(x)
		cmacd = calcMACDback(x)
		kdj = calcKDJ(x)
		ckdj = calcKDJback(x)
		ci = chaoDi(x)
		cbl = chaoBaoLuo(x)
		rcbl = realChaoBaoLuo(x)
		rsi5 = getRsi(x)
		vs = vs +av + upp + macd + cmacd + kdj + ckdj + rsi5 + ci + cbl + rcbl
		f.write(vs.decode('gbk'))
		f.write('</tr>')
		coo +=1


	f.write('</table>')

	f.close()


def calcKDJ(stockCode):
	#KDJ params is 9 , 3
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	#co = stock_data['quick_d'].count()
	sco = stock_data['slow_d'].count()
	yesterdayk = stock_data['quick_d'][co-2]
	k = stock_data['quick_d'][co-1]
	yesterdayd = stock_data['slow_d'][co-2]
	d = stock_data['slow_d'][co-1]
	if (yesterdayk < yesterdayd) and (k>=d):
		k1 = math.atan(d-yesterdayd)
		k2 = math.atan(k-yesterdayk)
		d1 = math.degrees(k1)
		d2 = math.degrees(k2)
		if d1<0:
			d1 = -d1
		return '<td><font color=red>KDJ</font>&nbsp;'+str(d1+d2)+'</td>'
	else:
		return '<td></td>'

def calcMACD(stockCode):
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	sco = stock_data['DEA'].count()
	yesterdayk = stock_data['DIFF'][co-2]
	k = stock_data['DIFF'][co-1]
	yesterdayd = stock_data['DEA'][co-2]
	d = stock_data['DEA'][co-1]
	if (yesterdayk < yesterdayd) and (k>=d):
		#get the angle
		k1 = math.atan(d-yesterdayd)
		k2 = math.atan(k-yesterdayk)
		d1 = math.degrees(k1)
		d2 = math.degrees(k2)
		if d1<0:
			d1 = -d1
		return '<td><font color=red>MACD</font>&nbsp;'+str(d1+d2)+'</td>'
	else:
		return '<td></td>'


def calcMACDback(stockCode):
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	l = range(1,co-1)
	l.reverse()
	if stock_data['DIFF'][co-1]>stock_data['DEA'][co-1]:
		jincha1 = co-1
		for x in l:
			if stock_data['DIFF'][x]<stock_data['DEA'][x]:
				#jincha dian
				jincha1 = x
				break
		sicha1 = jincha1-1
		l2 = range(1,jincha1)
		l2.reverse()
		for x in l2:
			if stock_data['DIFF'][x]>stock_data['DEA'][x]:
				#sicha1
				sicha1 = x
				break
		jincha2 = sicha1-1
		l3 = range(1,sicha1)
		l3.reverse()
		for x in l3:
			if stock_data['DIFF'][x]<stock_data['DEA'][x]:
				#jincha dian
				jincha2 = x
				break
		sicha2 = jincha2-1
		l4 = range(1,jincha2)
		l4.reverse()
		for x in l4:
			if stock_data['DIFF'][x]>stock_data['DEA'][x]:
				sicha2 = x
				break
		#get 2 low point
		difflow1 = stock_data['DIFF'][sicha2]
		date1 = sicha2
		for x in range(sicha2,jincha2):
			if difflow1>stock_data['DIFF'][x]:
				difflow1 = stock_data['DIFF'][x]
				date1 = x
		difflow2 = stock_data['DIFF'][sicha1]
		date2 = sicha1
		for x in range(sicha1,jincha1):
			if difflow2>stock_data['DIFF'][x]:
				difflow2=stock_data['DIFF'][x]
				date2 = x
		close1 = stock_data['low'][date1]
		close2 = stock_data['low'][date2]
		if (close1 <= close2) and (difflow1>difflow2):
			return '<td>macd back</td>'

	return '<td></td>'


def calcKDJback(stockCode):
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	l = range(1,co-1)
	l.reverse()
	if stock_data['quick_d'][co-1]>stock_data['slow_d'][co-1]:
		jincha1 = co-1
		for x in l:
			if stock_data['quick_d'][x]<stock_data['slow_d'][x]:
				#jincha dian
				jincha1 = x
				break
		sicha1 = jincha1-1
		l2 = range(1,jincha1)
		l2.reverse()
		for x in l2:
			if stock_data['quick_d'][x]>stock_data['slow_d'][x]:
				#sicha1
				sicha1 = x
				break
		jincha2 = sicha1-1
		l3 = range(1,sicha1)
		l3.reverse()
		for x in l3:
			if stock_data['quick_d'][x]<stock_data['slow_d'][x]:
				#jincha dian
				jincha2 = x
				break
		sicha2 = jincha2-1
		l4 = range(1,jincha2)
		l4.reverse()
		for x in l4:
			if stock_data['quick_d'][x]>stock_data['slow_d'][x]:
				sicha2 = x
				break
		#get 2 low point
		difflow1 = stock_data['quick_d'][sicha2]
		date1 = sicha2
		for x in range(sicha2,jincha2):
			if difflow1>stock_data['quick_d'][x]:
				difflow1 = stock_data['quick_d'][x]
				date1 = x
		difflow2 = stock_data['quick_d'][sicha1]
		date2 = sicha1
		for x in range(sicha1,jincha1):
			if difflow2>stock_data['quick_d'][x]:
				difflow2=stock_data['quick_d'][x]
				date2 = x
		close1 = stock_data['low'][date1]
		close2 = stock_data['low'][date2]
		if (close1 <= close2) and (difflow1>difflow2):
			return '<td>kdj back</td>'

	return '<td></td>'




def chaoDi(stockCode):
	#chao di
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	#per = stock_data['percent'][co-1]
	#print "percent:",per
	mco = stock_data['MA3'].count()
	eco = stock_data['EMA5'].count()
	todayclose = stock_data['close'][co-1]
	ma3 = stock_data['MA3'][co-1]
	#todayclose > 1.055*ma3 , low > ref(high,1) , v > ref(v,1)*1.2 , c > ma(c,5)
	ema5 = stock_data['EMA5'][co-1]
	todayv = stock_data['volume'][co-1]
	yesterdayv = stock_data['volume'][co-2]
	todaylow = stock_data['low'][co-1]
	yesterdayhigh = stock_data['high'][co-2]
	if (todayclose > ma3*1.055) and (todayclose > ema5) and (todaylow > yesterdayhigh) and (todayv > yesterdayv*1.2):
		return '<td><font color=red>Volume up, close bigger than Ma(3)</font></td>'
	else:
		return '<td></td>'


def chaoBaoLuo(stockCode):
	#chao guo baoluo xian
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	eco = stock_data['EMA14'].count()
	ema14 = stock_data['EMA14'][co-1]
	todayhigh = stock_data['high'][co-1]
	# high> 1.04*ema14,
	if (todayhigh > ema14*1.04):
		return '<td><font color=blue>high bigger than ema14*1.04, highest:' +str(todayhigh) +' ema14:'+ str(ema14) +'</font></td>'
	else:
		return '<td></td>'

def realChaoBaoLuo(stockCode):
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	eco = stock_data['EMA14'].count()
	mco = stock_data['MA3'].count()
	ema14 = stock_data['EMA14'][co-1]
	ma3 = stock_data['MA3'][co-1]
	lo = stock_data['low'][co-1]
	cp = ema14 - stock_data['EMA14'][co-2]
	lo2 = lo + cp
	# high> 1.04*ema14,
	if (ma3 > ema14*1.04):
		return '<td><font color=red>ma3 bigger than ema14*1.04, ma3:' + str(ma3) + '</font></td><td><font color=red>' + str(lo2) + '</font></td>'
	else:
		return '<td></td>' + '<td><font color=red>' + str(lo2) + '</font></td>'


def getRsi(stockCode):
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	rsi5 = stock_data['rsi5'][co-1]
	if rsi5<30:
		return '<td><font color=red>'+str(rsi5)+'</font></td>'
	else:
		return '<td>'+str(rsi5)+'</td>'


def getAmpli(stockCode):
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	#avp = stock_data['avgpriceema5'][co-1]
	avgdiff = stock_data['highlowdiffema5'][co-1]
	return '<td>avg high-low:' + str(avgdiff) +'</td>'

def get30daysup(stockCode):
	stock_data = pandas.read_csv(conf.tushare_download + '/' +stockCode+'_ewma.csv')
	co = stock_data['close'].count()
	it = 0
	xt = co-30
	if xt<0:
		return '<td></td>'
	for x in range(xt,co):
		if stock_data['percent'][x]*100>5:
			it +=1
	return '<td>'+str(it)+'</td>'




if __name__ == '__main__':

	print "start : ",time.strftime('%Y-%m-%d %X',time.localtime())
	#analyse()
	analyseMylist()
	print "finish : ",time.strftime('%Y-%m-%d %X',time.localtime())
