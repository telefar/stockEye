# coding: utf8
import tushare as ts
import time
#from EmailSender import EmailSender
import requests

CODE = {'518880':'黄金ETF',
        '159915':'创业板'}

CODE_28 = {'510500':'中证500',
        '510300':'沪深300'}

def get_hist_cur_price(code):
    hist_len = 20
    date = time.strftime("%Y-%m-%d")
    hist = ts.get_hist_data(code, start='2016-04-01',end=date)[hist_len:hist_len+1]
    hist_price = float(hist['close'])
    cur_price = float(ts.get_realtime_quotes(code)['price'])
    return hist_price, cur_price

def rotate(code_info):
    delta = {}
    for code in code_info:
        hist, now = get_hist_cur_price(code)
        delta[code] = ((now - hist) / hist * 100)

    max_code = None
    max_value = 0
    for code in delta:
        if delta[code] > max_value:
            max_code = code
            max_value = delta[code]

    result_str = ""
    for code in delta:
        result_str += "%s: %.2f%%\n\n" % (code_info[code], delta[code])

    choose = code_info[max_code] if max_code else "cash"
    result_str += "Hold: %s\n\n" % choose

    return result_str

def send(info):
    url = 'http://sc.ftqq.com/SCU7405T424616f07ef80ce90bd3696d7d39a73558ec2328efcb9.send'
    title = "轮动策略 %s" % time.strftime("%Y-%m-%d")
    data = {'text': title, 'desp':info}
    r = requests.post(url, data)

if __name__ == "__main__":
    #hist = ts.get_hist_data('600674', start='2016-04-01',end='2016-05-10')
    #print(hist)

    #print(rotate(CODE))
    #print(rotate(CODE_28))

    info = ""
    info += rotate(CODE)
    info += "\n\n---\n"
    info += rotate(CODE_28)
    print info

    send(info)
