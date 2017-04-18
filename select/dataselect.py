# -*- coding:utf-8 -*-
from pymongo import MongoClient
from stockclass import Stock
#from stockMain import stockView
from datetime import date, timedelta, datetime
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
import tushare as ts
import json
import logging
import math
import pandas
import config.Globaldata as conf
import os

def boolToInt(bool):
    if bool:
        return 1
    else:
        return 0

def floatFormat(num):
    if math.isnan(num):
        return 0.0
    else:
        return float(int(num*1000))/1000

def writeToJsonFileForTraining(dataArray):
    file = open("stock.json", "w")
    lastClose_bMds = []
    lastOpen_bMds = []
    lastClose_bUps = []
    lastOpen_bUps = []
    thisChanges = []
    thisOpen_bUps = []
    thisClose_bUps = []
    thisV_bs = []
    ifHengPans = []
    results = []


    for sample in dataArray:
        for day in sample.dates:
            conditionday = datetime.strptime(day, '%Y-%m-%d').date()
            todayindex = sample.indexof(conditionday)
            yesterdayindex = todayindex - 1
            nextdayindex = todayindex + 1
            if yesterdayindex > -1 and nextdayindex < len(sample.dates) and yesterdayindex > 20 and todayindex > 20:
                bMd = sample.bollMd(conditionday)
                bUp = sample.bollUp(conditionday)
                lastClose = sample.closePrices[yesterdayindex]
                lastOpen = sample.openPrices[yesterdayindex]
                thisChange = sample.changePrices[todayindex]
                thisOpen = sample.openPrices[todayindex]
                thisClose = sample.closePrices[todayindex]
                thisV_b = sample.v_b(sample.v_ma5[todayindex], sample.volume[todayindex])
                if bMd == 0.0 or bUp == 0.0:
                    continue
                lastClose_bMds.append(floatFormat((lastClose-bMd)/bMd))
                lastOpen_bMds.append(floatFormat((lastOpen-bMd)/bMd))
                lastClose_bUps.append(floatFormat((lastClose-bUp)/bUp))
                lastOpen_bUps.append(floatFormat((lastOpen-bUp)/bUp))
                thisChanges.append(floatFormat(sample.changePrices[todayindex]))
                thisOpen_bUps.append(floatFormat((thisOpen-bUp)/bUp))
                thisClose_bUps.append(floatFormat((thisClose-bUp)/bUp))
                thisV_bs.append(floatFormat(sample.v_b(sample.v_ma5[todayindex], sample.volume[todayindex])))
                ifHengPans.append(sample.checkIfHengPan(conditionday))
                results.append(sample.changePrices[nextdayindex] > 0.03 )
    jsonobj = {"result": results, "lastClose_bMd": lastClose_bMds, "lastOpen_bMd": lastOpen_bMds, "lastClose_bUp": lastClose_bUps, "lastOpen_bUp": lastOpen_bUps, "thisChange": thisChanges, "thisOpen_bUp": thisOpen_bUps, "thisClose_bUp": thisClose_bUps, "thisV_b": thisV_bs, "ifHengPan": ifHengPans}
    jsonstr = json.dumps(jsonobj, separators=(",", ": "))
    file.write(jsonstr)
    file.close()

def writeToArffFile(dataArray,filename):
    file = open(filename, "w")
    file.write("@relation stock\n")
    file.write("\n")
    dataexample = stockView()
    memberlist = [m for m in dir(dataexample)]
    attrs = []
    for m in memberlist:
        if m[0] != "_" and not callable(getattr(dataexample,m)):
            attrs.append(m)
    for attr in attrs:
        if attr != "result":
            file.write("@attribute {0} numeric\n".format(attr))
    file.write("@attribute {0} {{High, Low, MinusHigh, MinusLow}}\n".format("result"))
    file.write("\n")
    file.write("@data\n")
    total = len(dataArray)
    prog = 0
    for idx, sample in enumerate(dataArray):
        if int((idx+1)*100/total) > prog:
            print("{0}\tOutput: {1}%\n".format(datetime.now().strftime("%d %b %Y %H:%M:%S"), int((idx+1)*100/total)))
            prog = (idx+1)*100/total
        for day in sample.dates:
            conditionday = datetime.strptime(day, '%Y-%m-%d').date()
            data = stockView().fromStock(sample, conditionday)
            if data != None:
                attrvalues = []
                for attr in attrs:
                    if attr != "result":
                        attrvalues.append(getattr(data, attr))
                file.write("{{0 {0[0]}, 1 {0[1]}, 2 {0[2]}, 3 {0[3]}, 4 {0[4]}, "
                           "5 {0[5]}, 6 {0[6]}, 7 {0[7]}, 8 {0[8]}, 9 {1}}}\n".format(attrvalues, data.result))
    file.close()

def fetchDataOneThread(prefix, startday, endday):
    data = []
    for index in range(pow(10,(6-len(prefix)))):
        suffix = str(index).zfill(6-len(prefix))
        stockId = prefix + suffix
        try:
            result = ts.get_hist_data(stockId, start=startday.isoformat(),end=endday.isoformat())
            stock = Stock()
            stock.id = stockId
            stock.dates = result.index.tolist()
            stock.openPrices = result.open.values.tolist()
            stock.closePrices = result.close.values.tolist()
            stock.v_ma5 = result.v_ma5.values.tolist()
            stock.volume = result.volume.tolist()
            stock.PChange()
            data.append(stock)
        except Exception as e:
            print (e)
            if str(e).find("list index out of range") > -1:
                logging.warning(str(e))
            print (stockId + " is not a valid stock.\n")
    return data

# with qian fu quan
def fetchDataOneThreadwithFQ(prefix, startday, endday):
    data = []
    for index in range(pow(10,(6-len(prefix)))):
        suffix = str(index).zfill(6-len(prefix))
        stockId = prefix + suffix
        try:
            result = ts.get_h_data(stockId, start=startday.isoformat(),end=endday.isoformat())
            stock = Stock()
            stock.id = stockId
            dates = result.index.tolist()
            for day in dates:
                stock.dates.append(day.date().isoformat())
            stock.openPrices = result.open.values.tolist()
            stock.closePrices = result.close.values.tolist()
            stock.volume = result.volume.tolist()
            stock.calc_v_ma5()
            stock.PChange()
            data.append(stock)
        except Exception as e:
            print (e)
            if str(e).find("list index out of range") > -1:
                logging.warning(str(e))
            print (stockId + " is not a valid stock.\n")
    return data

def fetchToday(stocks):
    today = date.today()
    stocksnow = ts.get_today_all()
    codes = stocksnow.code.tolist()
    for stock in stocks:
        stockidx = -1
        for codeidx, code in enumerate(codes):
            if stock.id == code:
                stockidx = codeidx
                break
        if stockidx > -1:
            stock.name = stocksnow.name.tolist()[stockidx]
            if len(stock.dates) - 1 < 0:
                continue
            if today.isoformat() != stock.dates[len(stock.dates) - 1]:
                if len(stock.closePrices) - 1 < 0:
                    continue
                stock.dates.append(today)
                stock.openPrices.append(stocksnow.open.tolist()[stockidx])
                stock.closePrices.append(stocksnow.trade.tolist()[stockidx])
                if stocksnow.open.tolist()[stockidx] == 0.0:
                    stock.changePrices.append(0.0)
                else:
                    stock.changePrices.append((stocksnow.trade.tolist()[stockidx] - stocksnow.open.tolist()[stockidx])/stocksnow.open.tolist()[stockidx])
                stock.volume.append(stocksnow.volume.tolist()[stockidx])
                idx = stock.indexof(today)
                if idx >= 4:
                    stock.v_ma5.append((stock.volume[idx] + stock.volume[idx - 1] + stock.volume[idx - 2] + stock.volume[idx - 3] + stock.volume[idx - 4])/5)
                else:
                    total = 0
                    i = 0
                    while(i<=idx):
                        total += stock.volume[idx - i]
                        i += 1
                    stock.v_ma5.append(total/(idx + 1))

def fetchData(dataPrefix, startday, endday):
    data = []
    arg = []
    pool = ThreadPool(len(dataPrefix))
    partial_fetch_data_one_thread_with_fq = partial(fetchDataOneThreadwithFQ, startday=startday, endday=endday)
    # results = pool.map(fetchDataOneThread, arg)
    results = pool.map(partial_fetch_data_one_thread_with_fq, dataPrefix)
    pool.close()
    pool.join()
    for result in results:
        data.extend(result)
    # fetchToday(data)
    return data

def storeData(prefix, startday, endday, client):
    data = []
    database = client["stock"]
    newlastday = None
    newbeginday = None
    for index in range(pow(10,(6-len(prefix)))):
        suffix = str(index).zfill(6-len(prefix))
        stockId = prefix + suffix
        try:
            results = ts.get_h_data(stockId, start=startday.isoformat(),end=endday.isoformat())
            results["stockId"] = Series([stockId for x in range(len(results.index.tolist()))], index = results.index)
            results["date"] = Series([x.date().isoformat() for x in results.index.tolist()], index = results.index)
            ticks = database.ticks
            if ticks is None:
                database.create_collection("ticks")
                ticks = database.ticks
            # tick = ticks.find_one({"stockId": stockId, "date":{'$gte': startday.isoformat(),'$lte': endday.isoformat()}})
            # if tick == None:
            print (stockId + " data required.\n")
            ticks.insert(json.loads(results.to_json(orient='records')))
            dates = results.index.tolist()
            if newlastday is None or newlastday < dates[0].date():
                newlastday = dates[0].date()
            if newbeginday is None or newbeginday < dates[len(dates) - 1].date():
                newbeginday = dates[len(dates) - 1].date()
        except Exception as e:
            print (e)
            if str(e).find("list index out of range") > -1:
                logging.warning(str(e))
            print (stockId + " is not a valid stock.\n")
    profilecollections = database.profile
    profile = profilecollections.find_one()
    if newlastday is None:
        if profile is None:
            profilecollections.update_one({'_id': profile['_id']}, {'$set': {'lastupdateday': newlastday.isoformat()}})
        else:
            profilecollections.insert_one({'lastupdateday': newlastday.isoformat()})
    profile = profilecollections.find_one()
    if newbeginday is None:
        if profile is None:
            profilecollections.update_one({'_id': profile['_id']}, {'$set': {'beginupdateday': newbeginday.isoformat()}})
        else:
            profilecollections.insert_one({'beginupdateday': newbeginday.isoformat()})

def getDataFromMongoOnethread(prefix, startday, endday):

    data = []
    for stockCode in conf.myStlist:
        filename = conf.tushare_download +'./%s.csv'%stockCode
        if os.path.exists(filename):
            stockData = pandas.read_csv(filename)
        else:
            continue

        stock = Stock()
        stock.id = stockCode
        '''
        for result in stockData:
            stock.dates.append(eval(result['date']))
            stock.openPrices.append(float(result['open']))
            stock.closePrices.append(float(result['close']))
            stock.volume.append(result['volume'])
		'''

        stock.dates.extend(stockData['date'])
        stock.openPrices.extend(stockData['open'])
        stock.closePrices.extend(stockData['close'])
        stock.volume.extend(stockData['volume'])

        stock.calc_v_ma5()
        stock.PChange()

        data.append(stock)
        #logging.warning(str(e))

    return data
    '''
    client =MongoClient(host='localhost', port=27017, maxPoolSize=None)
    db = client["stock"]
    profilecollections = db.profile
    if profilecollections is None:
        db.create_collection("profile")
        profilecollections = db.profile
    profile = profilecollections.find_one()

    fetch_endday = endday
    fetch_starday = startday

    if profile is not None:
        beginday = datetime.strptime(profile['beginupdateday'], '%Y-%m-%d').date()
        lastday = datetime.strptime(profile['lastupdateday'], '%Y-%m-%d').date()
        # if fetch_endday >= beginday:
        #    fetch_endday = beginday - timedelta(days=1)
        if fetch_starday <= lastday:
            fetch_starday = lastday + timedelta(days=1)

    if fetch_starday <= fetch_endday:
        partial_storeData = partial(storeData, startday=fetch_starday, endday=fetch_endday, client = client)
        pool = ThreadPool(len(dataPrefix))
        pool.map(partial_storeData, dataPrefix)
        pool.close()
        pool.join()


    data = []
    pool = ThreadPool(len(dataPrefix))
    partial_getDataFromMongoOnethread = partial(getDataFromMongoOnethread, startday=startday, endday=endday)
    results = pool.map(partial_getDataFromMongoOnethread, dataPrefix)
    pool.close()
    pool.join()
    for result in results:
        data.extend(result)

    data = []
    # fetchToday(data)
    data = getDataFromMongoOnethread(dataPrefix,startday, endday)
    return data
	'''

'''
prefixes = ['6000','6001','6002','6003','6004','6005','6006','6007','6008','6009', '6010', '6011', '6012', '6013', '6014', '6015', '6016', '6017',  '6018', '6019', '6030', '6031', '6032', '6033', '6034', '6035', '6036', '6037', '6038', '6039', '0020','0021','0022','0023','0024','0025','0026','0027','0028','0029']
#prefixes = ['60030']

startday = datetime.strptime("2010-01-01", '%Y-%m-%d').date()
endday = datetime.strptime("2014-05-28", '%Y-%m-%d').date()
stocks = fetchData_mongo(prefixes, startday, endday)
'''
