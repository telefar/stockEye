from bs4 import BeautifulSoup as BS
import requests, time

CODE_LIST = [270049, '000299', '001338', '001511']

def get_fund_val(code):
    url = 'http://fund.eastmoney.com/%s.html' % code
    page = requests.get(url)

    if not page.ok:
        print 'http get failed'
        return None

    soup = BS(page.content, 'lxml')

    tmp = []
    for c in soup.find_all('div', attrs={'class':'SitePath'})[0].children:
        tmp.append(c.string)

    name = tmp[-1]
    n = soup.find_all(attrs= {'class':"dataItem02"})

    result = name + ' '
    for nn in n:
        result += nn.dt.p.text.split(' ')[1] + ' '
        #print nn.find_all(attrs={'class':'ui-font-large ui-color-green ui-num'})
        for c in nn.dd.children:
            result += c.text + ' '
        #print nn.find_all('span', attrs = {'class':"ui-font-middle ui-num"})

    return result

def send(info):
     url = 'http://sc.ftqq.com/SCU1113T3c238e0213b2b1185d9447b90731b69e57334055b295f.send'
     title = "fund value %s" % time.strftime("%Y-%m-%d")
     data = {'text': title, 'desp':info}
     r = requests.post(url, data)

try_num = 0

while try_num < 5:
    try:
        info = ''
        for code in CODE_LIST:
            info += get_fund_val(code) + "\n\n"

        break
    except:
        try_num += 1

print info
send(info)
