# -*-coding:utf-8-*-

__author__ = 'phabio.liu@aliyun.com'

import tushare as ts
import pandas as pd
import pylab as plt

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
===��ʱ==============================
'''
def warningOnEndDayOfMonth():
    #��ĩ�ʽ������ 20��-25�� action:sale

    todayRef = datetime.today()
    warningDayofMonth = datetime(todayRef.year,todayRef.month,20)
    actualToday = datetime.now().strftime('%Y-%m-%d')
    if todayRef < warningDayofMonth:
        print('-safety day',actualToday)
    elif todayRef > warningDayofMonth:
        print('-warning, end day of month %d, sale',actualToday)

#==================================================
#������ȯ���ף���ָͶ���������������ȯҵ���ʸ��֤ȯ��˾�ṩ����������ʽ�����֤ȯ�����ʽ��ף������֤ȯ����������ȯ���ף�����Ϊ������ȯ�̶�Ͷ���ߵ����ʡ���ȯ�ͽ��ڻ�����ȯ�̵����ʡ���ȯ��
#�������ָ���������Ʊ���볥�����ʶ�Ĳ��������������ʱ����ʾͶ������̬ƫ���򷽣��г�������ʢ����ǿ���г�����֮�����������г���
#��ȯ���ָ��ȯ��������ÿ�ճ�����ȯ��Ĳ���ȯ������ӣ���ʾ�г����������г�����֮�������򷽡�
"""
����˵����
?start:��ʼ���� format��YYYY-MM-DD Ϊ��ʱȡȥ�����
?end:�������� format��YYYY-MM-DD Ϊ��ʱȡ��ǰ����
?retry_count���������쳣�����Դ�����Ĭ��Ϊ3
?pause:����ʱͣ��������Ĭ��Ϊ0

����ֵ˵����
?opDate:���ý�������
?rzye:�����������(Ԫ)
?rzmre: �������������(Ԫ)
?rqyl: ������ȯ����
?rqylje: ������ȯ�������(Ԫ)
?rqmcl: ������ȯ������
?rzrqjyzl:����������ȯ���(Ԫ)
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
����������ȯ��������

����˵����
?start:��ʼ���� format��YYYY-MM-DD Ϊ��ʱȡȥ�����
?end:�������� format��YYYY-MM-DD Ϊ��ʱȡ��ǰ����
?retry_count���������쳣�����Դ�����Ĭ��Ϊ3
?pause:����ʱͣ��������Ĭ��Ϊ0

����ֵ˵����
?opDate:���ý�������(index)
?rzmre: ���������(Ԫ)
?rzye:�������(Ԫ)
?rqmcl: ��ȯ������
?rqyl: ��ȯ����
?rqye: ��ȯ����(Ԫ)
?rzrqye:������ȯ���(Ԫ)

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
����˵����
?year:���(YYYY),Ĭ��Ϊ��ǰ���

����ֵ˵����
?date:����
?ON:��ҹ�������
?1W:1�ܲ������
?2W:2�ܲ������
?1M:1���²������
?3M:3���²������
?6M:6���²������
?9M:9���²������
?1Y:1��������

"""
#todo tobe visualized
def shibor():
    df = ts.shibor_data() #ȡ��ǰ��ݵ�����
    #df = ts.shibor_data(2014) #ȡ2014�������
    info = df.sort('date', ascending=False).head(10)
    title = "last 10 shibor"
    print title
    print info
    info.to_csv('report.csv')
    return title, info

if __name__ == '__main__':
    print "start : ",time.strftime('%Y-%m-%d %X',time.localtime())
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

