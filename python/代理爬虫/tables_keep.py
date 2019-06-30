#!-*- coding=utf-8 -*-
from proxy.text import *
import threading
from crawler.crawler import *
sys.path.append("/Users/wangzeqing/Desktop/python/玩玩/bilibili")
from db.dborder import *
lock = threading.Lock()
dbcon = mysqlconnect(lock)
p = threading.Thread(target=dbcon.print_list)
p.start()

print("+++++++++++++++++++++++++++++++++++\n开始验证proxy表中的数据")
#kong('proxy',dbcon)
print("+++++++++++++++++++++++++++++++++++\n开始爬虫进程")
crawler('proxy',dbcon)
print("+++++++++++++++++++++++++++++++++++\n开始测试temporary中的数据")
kong('temporary',dbcon)
print("+++++++++++++++++++++++++++++++++++\n开始验证recycle表中的数据")
kong('recycle',dbcon)





