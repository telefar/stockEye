#coding:utf-8
import tushare as ts
from sqlalchemy import create_engine


def update_market():
    df = ts.get_today_all()
    #engine = create_engine('mysql://root:1234@127.0.0.1/stock_1?charset=utf8',encoding='gbk',convert_unicode=True)
    engine = create_engine('mysql://root:1234@127.0.0.1/stock_1',convert_unicode=True)
    #存入数据库
    df.to_sql('current_market',engine,flavor='mysql',if_exists='replace')
    print("Done")

