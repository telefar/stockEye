# -*-coding:utf-8-*-

__author__ = 'phabio.liu@aliyun.com'

import tushare as ts
import pandas as pd
import pylab as plt
import json

from datetime import datetime
from datetime import timedelta
import time

from helper.mail import *
from helper.Send2WeChatPublic import *
from select.stockMain import mystockSelection
from DataUpdate.downstock import downloadDailyStockData
from strategy.rotatePolicy import rotateStrategy
from analyse.calcstock import analyseMylist

'''
===???==============================
'''
def warningOnEndDayOfMonth():
    #??????????? 20??-25?? action:sale

    todayRef = datetime.today()
    warningDayofMonth = datetime(todayRef.year,todayRef.month,20)
    actualToday = datetime.now().strftime('%Y-%m-%d')
    if todayRef < warningDayofMonth:
        print('-safety day',actualToday)
    elif todayRef > warningDayofMonth:
        print('-warning, end day of month %d, sale',actualToday)

#==================================================
#???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
#??????????????????????????????????????????????????????????????????г????????????????г?????????????????г???
#??????????????????????????????????????????????г??????????г????????????????
"""
?????????
?start:??????? format??YYYY-MM-DD ???????????
?end:???????? format??YYYY-MM-DD ????????????
?retry_count?????????????????????????3
?pause:??????????????????0

??????????
?opDate:???y???????
?rzye:???????????(?)
?rzmre: ?????????????(?)
?rqyl: ???????????
?rqylje: ??????????????(?)
?rqmcl: ?????????????
?rzrqjyzl:??????????????(?)
"""
#http://blog.csdn.net/fennvde007/article/details/37693523
def rongZiRongQuanSh():
    #dat = ts.sh_margins(start=lastTwentyDays, end=ct._TODAY_)
    dat = ts.sh_margins()


    #xAxisOpdate[:10].rzye.plot(kind='barh',color='g',stacked=False)
    #xAxisOpdate[:10].rqylje.plot(kind='barh',color='b',stacked=False)

    xAxisOpdate = pd.DataFrame(dat,columns=['opDate','rzye','rqylje'])
    xAxisOpdatePlt = xAxisOpdate.set_index('opDate')
    xAxisOpdatePlt[:10].rzye.plot(kind='bar',color='g',width=0.8,stacked=False)
    xAxisOpdatePlt[:10].rqylje.plot(kind='bar',color='b',width=0.8,stacked=False)
    #xAxisOpdatePlt[:10].plot(kind='bar',color='g',width=0.8,stacked=False)
    #for x,y in zip(X,Y1):
    #    plt.text(x+0.3, y+0.05, '%.2f' % y, ha='center', va= 'bottom')

    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Shanghai Rongzi Rongquan Yu E')
    plt.show()
    #rongZiYuE = dat['rzye']
    #rongQuanYuE = dat['rqylje']


"""
???????????????????

?????????
?start:??????? format??YYYY-MM-DD ???????????
?end:???????? format??YYYY-MM-DD ????????????
?retry_count?????????????????????????3
?pause:??????????????????0

??????????
?opDate:???y???????(index)
?rzmre: ?????????(?)
?rzye:???????(?)
?rqmcl: ?????????
?rqyl: ???????
?rqye: ???????(?)
?rzrqye:??????????(?)

ts.sz_margins(start='2015-01-01', end='2015-04-19')

"""
def rongZiRongQuanSz():
    lastSeventeenDays = datetime.now() - timedelta(17)
    todayRef = datetime.now().strftime('%Y-%m-%d')
    dat = ts.sz_margins(start=lastSeventeenDays, end = todayRef)
    xAxisOpdate = dat.set_index('opDate')

    xAxisOpdate[:10].rzye.plot(kind='bar',color='g',stacked=False)
    xAxisOpdate[:10].rqye.plot(kind='bar',color='b',stacked=False)

    #for x,y in zip(X,Y1):
    #    plt.text(x+0.3, y+0.05, '%.2f' % y, ha='center', va= 'bottom')

    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Shenzhen Rongzi Rongquan Yu E')
    plt.show()

"""
?????????
?year:???(YYYY),??????????

??????????
?date:????
?ON:??????????
?1W:1????????
?2W:2????????
?1M:1???2??????
?3M:3???2??????
?6M:6???2??????
?9M:9???2??????
?1Y:1????????

"""
#todo tobe visualized
def shibor():
    df = ts.shibor_data() #????????????
    #df = ts.shibor_data(2014) #?2014???????
    info = df.sort_values('date', ascending=False).head(10)
    title = "last 10 shibor"
    print title
    #print info


    infostr = info.to_string()
    infoline ='\n'
    for i in infostr:
        if i== '\n':
            infoline.join("\n")
        infoline.join(i)
        print i
    print infoline
    raw_input()
    info.to_csv('report.csv')
    return title, info

if __name__ == '__main__':
    print "start : ",time.strftime('%Y-%m-%d %X',time.localtime())
    shibor()
    warningOnEndDayOfMonth()
    rongZiRongQuanSh()
    rongZiRongQuanSz()
    title,info = shibor()

    send2WeChatPublicByCsv(title, info)
    #send2WeChatPublic(title, info)
    rotateStrategy()
    downloadDailyStockData()
    mystockSelection()
    analyseMylist()



