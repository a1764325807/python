#!-*- coding=utf-8 -*-
import urllib2
import threading
import sys
import time
import ctypes
import inspect
sys.path.append("/Users/wangzeqing/Desktop/python/玩玩/bilibili")
from db.dborder import *


def kong(tables,dbcons):
	global dbcon
	dbcon = dbcons
	row = dbcon.table_all_select(tables,';')
	for list in row:
		proxy_support = urllib2.ProxyHandler({"https": "https://"+str(list[1])+':'+str(list[2])})
		opener = urllib2.build_opener(proxy_support)
		urllib2.install_opener(opener)
		#https_text(list,urllib2)
	#"""
		t = threading.Thread(target=dbcon.https_text,args=(list,urllib2,tables))
		t.start()
		while threading.activeCount() >100:  #防止文件打开数量超过系统最大设置这个值linux ulimit -n可以查看 windows暂时不清楚
			#print "超过最大线程数量"+str(threading.activeCount())
			time.sleep(2)
	#"""
	while threading.activeCount() != 2:
		print "剩下"+str(threading.activeCount())+"条进程未结束"
		time.sleep(10)
	
if __name__ == "__main__":
	kong('temporary')





