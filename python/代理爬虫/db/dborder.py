#!-*- coding=utf-8 -*-
# 作者：泽同学
# blog：www.orze.top
import pymysql
import re
import dbconfig
import random
import time
import datetime
import ctypes
import inspect
from gzip import GzipFile
from StringIO import StringIO
class mysqlconnect:
	def __init__(self,lock):
		self.lock = lock
		self.starttime = time.time()
		self.conn = 0
		self.statistical = dbconfig.statistical
		try:
			self.db = pymysql.connect(dbconfig.dbip,dbconfig.dbname,dbconfig.dbpass)
		except:
			exit("database connect error")
		self.con = self.db.cursor()
		#self.con.execute('')
		self.lock.acquire()
		self.con.execute('select version();')
		self.lock.release()
		data = self.con.fetchone()
		print("database connect successful Version:"+data[0])
		confirm = self.databases_exists()
		if confirm:
			print confirm
		for table_name in dbconfig.tables_name_proxy:
			confirm = self.table_exists(table_name)
			if confirm:
				print confirm
	
	def databases_exists(self):  #检测数据库是否存在
		self.lock.acquire()
		self.con.execute("show databases;")
		self.lock.release()
		data = self.con.fetchall()
		databases_list = re.findall('(\'.*?\')',str(data))
		databases_list = [re.sub("'",'',each) for each in databases_list]
		if "proxy" in databases_list:
			self.lock.acquire()
			self.con.execute("use proxy;")
			self.lock.release()
			return
		else:
			self.lock.acquire()
			self.con.execute("create database proxy;")
			self.lock.release()
			self.lock.acquire()
			self.con.execute("use proxy;")
			self.lock.release()
			return("proxy数据库创建完成")
	
	def table_exists(self,table_name): #检测表是否存在
		self.lock.acquire()
		self.con.execute("show tables;")
		self.lock.release()
		data = self.con.fetchall()
		table_list = re.findall('(\'.*?\')',str(data))
		table_list = [re.sub("'",'',each) for each in table_list]
		if table_name in table_list:
			return
		else:
			if table_name == dbconfig.tables_name_proxy[0] or table_name == dbconfig.tables_name_proxy[1]:
				sql = """CREATE TABLE %s (
					id  int(8)  not null  primary key  auto_increment,
					ip  CHAR(20) not null,
					port INT(5) not null,
					type INT(1) not null,  #0http 1https 2 socket
					level INT(1) not null,
					delay float(5,3) not null,
					time CHAR(20) not null,
					INDEX (ip,port,type)
					);
				"""%(table_name)
			elif table_name in dbconfig.tables_name_proxy[2] or table_name == dbconfig.tables_name_proxy[3]:
				sql = """CREATE TABLE %s (
					id  int(8)  not null  primary key  auto_increment,
					ip  CHAR(20) not null,
					port INT(5) not null,
					type INT(1),
					level INT(1) not null,
					url CHAR(20) not null,
					time CHAR(20) not null,
					INDEX (ip,port,type,url)
					);
				"""%(table_name)

			self.lock.acquire()
			self.con.execute(sql)
			self.lock.release()
			return (str(table_name)+"表已经构造完成")
			
	def get_header(self):
		heads= {
						'User-Agent': random.choice(dbconfig.USER_AGENTS),
						'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Accept-Language': 'en-US,en;q=0.5',
						'Connection': 'keep-alive',
						'Accept-Encoding': 'gzip, deflate',
						}
		return heads
			
	installs = 0
	true_installs = 0
	false_installs = 0
	url_install = {}
	for urllist in dbconfig.urllist:
		url_install[urllist['name']] = 0
	def table_install(self,data,tables):
		if tables == dbconfig.tables_name_proxy[0] or tables == dbconfig.tables_name_proxy[1]:
			sql = "INSERT INTO "+tables+" (ip,port,type,level,delay,time) values (%s,%s,%s,%s,%s,%s);"
		elif tables == dbconfig.tables_name_proxy[3] or tables == dbconfig.tables_name_proxy[2]:
			sql = "INSERT INTO "+tables+" (ip,port,type,level,url,time) values (%s,%s,%s,%s,%s,%s);"
			self.url_install[data[4]]+=1
		#print sql % data
		self.lock.acquire()
		self.con.execute(sql,data)
		self.lock.release()
		self.lock.acquire()
		self.db.commit()
		self.lock.release()
		self.statistical['installs'][tables]+=1
		return self.con.rowcount
	true_updates = 0
	false_updates = 0
	def table_update(self,data,tables):
		sql = "UPDATE "+tables+" SET %s = '%s' WHERE id = '%s';"
		#if not tables == 'temporary':
		#	print sql % data
		self.lock.acquire()
		self.con.execute(sql%data)
		self.lock.release()
		self.lock.acquire()
		self.db.commit()
		self.lock.release()
		self.statistical['updates'][tables]+=1
		return self.con.rowcount
	true_deletes = 0
	false_deletes = 0
	temporary_deletes = 0
	def table_delete(self,data,tables):
		sql = "DELETE FROM "+tables+" WHERE id = %s;"
		#if not tables == 'temporary':
		#	print sql % data
		self.lock.acquire()
		self.con.execute(sql,data)
		self.lock.release()
		self.lock.acquire()
		self.db.commit()
		self.lock.release()
		self.statistical['deletes'][tables]+=1
		return self.con.rowcount
	selects = 0
	def table_select(self,data,tables):
		sql = "SELECT * FROM "+tables+" WHERE ip = %s and port = %s and type = %s;"
		#print sql % data
		self.lock.acquire()
		self.con.execute(sql,data)
		self.lock.release()
		self.statistical['selects'][tables]+=1
		#return self.con.fetchall()  #查看
		return (self.con.rowcount,self.con.fetchall())
	def table_all_select(self,tables,data):
		sql = "SELECT * FROM "+tables+" "+data
		#print sql
		self.lock.acquire()
		self.con.execute(sql)
		self.lock.release()
		return(self.con.fetchall())
		
	def _async_raise(self,tid, exctype):
	    """raises the exception, performs cleanup if needed"""
	    tid = ctypes.c_long(tid)
	    if not inspect.isclass(exctype):
	        exctype = type(exctype)
	    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
	    if res == 0:
	        raise ValueError("invalid thread id")
	    elif res != 1:
	        # """if it returns a number greater than one, you're in trouble,
	        # and you should call it again with exc=NULL to revert the effect"""
	        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
	        raise SystemError("PyThreadState_SetAsyncExc failed")
	 
	def stop_thread(self,thread):
	    self._async_raise(thread.ident, SystemExit)


	def print_list(self):
		while 1:
			time.sleep(10)
			with open('proxy.log','w') as f:
				for prints in self.statistical:
					f.write(str(prints)+'\n')
					for i in self.statistical[prints]:
						f.write(str(i)+':')
						f.write(str(self.statistical[prints][i])+',')
					f.write('\n')
				for x in self.url_install:
					f.write(str(x)+':')
					f.write(str(self.url_install[x])+'\n')
				f.write("当前以运行"+str(int(time.time()-self.starttime)/60)+"分钟")
				f.close()
		
	
	def gzip1(self,data):   #gzip解码
		buf = StringIO(data)  #进行转换
		f = GzipFile(fileobj=buf)
		return f.read()
		
	def https_text(self,list,urllib2,deltables):
		url="https://www.baidu.com"
		req = urllib2.Request(url,headers=self.get_header())
		delay =0 
		for i in range(3):
			try:
				itime=time.time()
				data=urllib2.urlopen(req,timeout = 20)
				delay = "%.3f"%(time.time()-itime)
				break
			except Exception as a:
				try:
					a.args[0]
				except:
					continue
				if  str(a.args[0]) == '[Errno 61] Connection refused':
					break
				elif str(a.args[0]) == '[Errno 51] Network is unreachable':
					print "你的网络可能没有连接好请测试后启动。"
					return
				elif str(a.args[0]) == '[Errno 65] No route to host':
					print "你的网关可能没有连接好请测试后启动。"
					return
		if delay > 0:
			self.true_db(list,delay)
		elif delay ==0:
			self.false_db(list)
		if deltables == 'temporary':
			self.table_delete(list[0],deltables)


	def true_db(self,list,delay):
		data=(list[1],list[2],'1')  #可以访问则进行
		row = self.table_select(data,"proxy")
		if row[0] == 0:	#无的话就插入新信息
			now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			data = (list[1],list[2],'1','5',delay,now_time)
			self.table_install(data,"proxy")
			#print "proxy表中插入了"+str(row)+"条信息"
		elif row[0] == 1:
			if row[1]:
				#print delay,row[1][0][4]
				data=('delay',delay,row[1][0][0])
				self.table_update(data,"proxy")
				now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				data=('time',now_time,row[1][0][0])
				self.table_update(data,"proxy")
				#print "proxy表中修改了"+str(row)+"条信息"
			else:
				print "proxy查询中出现了点小问题不用在意"+str(list)+str(row)
		else:
			dbcon.table_delete(row[1][1][0],'proxy')
			print "成功清除proxy中重复id"+str(row[1][1][0])
		data=(list[1],list[2],'1')  #可以访问则进行
		row = self.table_select(data,"recycle")
		if row[0] == 0:
			pass
		elif row[0] == 1:
			self.table_delete(row[1][0][0],"recycle")
		else:
			self.table_delete(row[1][1][0],'recycle')
			print "成功清除recycle中重复id"+str(row[1][1][0])
			
	def false_db(self,list):
		data=(list[1],list[2],'1')  #不可以访问则进行
		row = self.table_select(data,"recycle")
		if row[0] == 0:
			now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			data = (list[1],list[2],'1','5','2',now_time)
			self.table_install(data,"recycle")
			#print "回收站中插入了"+str(row)+"条信息"
		elif row[0] == 1:
			if row[1]:
				if str(row[1][0][5]-1) <= 0:
					self.table_delete(row[1][0][0],"recycle")
				else:
					data=('delay',(row[1][0][5]-1),row[1][0][0])
					row = self.table_update(data,"recycle")
			#print "回收站中修改了"+str(row)+"条信息"
			else:
				print "recycle查询中出现了点小问题不用在意"
				print list
				print row
		else:
			self.table_delete(row[1][1][0],'recycle')
			print "成功清除recycle中重复id"+str(row[1][1][0])
		data=(list[1],list[2],'1')  #不可以访问则进行
		row = self.table_select(data,"proxy")
		if row[0] == 0:
			pass
		elif row[0] == 1:
			if row[1]:
				self.table_delete(row[1][0][0],"proxy")
		else:
			self.table_delete(row[1][1][0],'proxy')
			print "成功清除proxy中重复id"+str(row[1][1][0])