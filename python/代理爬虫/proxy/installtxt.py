#!-*- coding=utf-8 -*-
import sys
sys.path.append("..")
from db.dborder import *
import threading
lock = threading.Lock()
dbcon = mysqlconnect(lock)
import datetime
with  open("proxy.txt",'r') as f:
	for list in f.readlines():
		data=(list.split(':')[0],list.split(':')[1].strip('\n'),'5')
		row = dbcon.table_select(data,"temporary")
		if row[0] == 0:
			now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			data = (list.split(':')[0],list.split(':')[1].strip('\n'),'5','5','?',now_time)
			dbcon.table_install(data,"temporary")

