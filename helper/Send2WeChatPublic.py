# coding: utf8

import time
import requests


def send2WeChatPublic(title, info):
    url = 'http://sc.ftqq.com/SCU7405T424616f07ef80ce90bd3696d7d39a73558ec2328efcb9.send'
    titles = title + "(" + "%s" % time.strftime("%Y-%m-%d") +")"
    data = {'text': titles, 'desp':info}
    r = requests.post(url, data)

def send2WeChatPublicByCsv(title, sendfile):
    url = 'http://sc.ftqq.com/SCU7405T424616f07ef80ce90bd3696d7d39a73558ec2328efcb9.send'
    titles = title + "(" + "%s" % time.strftime("%Y-%m-%d") +")"

    files = {'file': (sendfile, titles)}
    r = requests.post(url, files)

#demo
if __name__ == "__main__":

    title = "my title-标题党"
    info = "test"
    info += "\n\n---\n"

    print info

    #send2WeChatPublic(title, info)
    send2WeChatPublicByCsv(title, info)
