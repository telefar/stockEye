#coding:utf-8
__author__ = 'phabio'


import MySQLdb

#-----------MySQL测试代码-------------

def mysql_test():
    try:
        sql='select * from proc'
        conn=MySQLdb.connect(host='127.0.0.1',user='root',passwd='1234',db='mysql',port=3306)
        cur=conn.cursor()
        cur.execute(sql)
        print 'conn:%s' %conn
        print 'cur: %s' %cur
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print 'MySQL Error %d:%s' %(e.args[0],e.args[1])

def check_create_database(request):
    #dbname = request.POST.get("dbname")
    #databasename = request.POST.get('databasename')
    #table_name = request.POST.get('table')
    dbname = "stock_1.0"
    conn = MySQLdb.connect(host='localhost', user='root',passwd='1234')
    #获取操作游标
    cursor = conn.cursor()
    #执行SQL,创建一个数据库.
    cursor.execute("create database %s" % dbname)
    #执行SQL,进入数据库.
    cursor.execute("use %s" % db_name)
    #执行SQL,建立数据库表.
    #cursor.execute("create table %s (id int(5) not null primary key auto_increment,create_user int(5),create_date date)" % table_name)
    #关闭连接，释放资源
    cursor.close();
    msg = '成功建立数据库:'+dbname
    print msg
    #url = '/carbon/browser_database/'
    #return render_to_response('operation.html',locals())

if __name__=="__main__":
    mysql_test()
    print "test ok!"
    check_create_database(0)
