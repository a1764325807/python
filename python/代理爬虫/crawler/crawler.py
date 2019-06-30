#!-*- coding=utf-8 -*-
import urllib2
import threading
import sys
import time
import datetime
import time
import re
import requests
from selenium import webdriver
sys.path.append("/Users/wangzeqing/Desktop/python/玩玩/bilibili")
from db.dborder import *
import db.dbconfig

def COOKIES(url,ip):
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--headless')
	#chrome_options.add_argument("--proxy-server="+ip)
	chrome_options.add_argument('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"')	
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('blink-settings=imagesEnabled=false')
	driver=webdriver.Chrome(chrome_options=chrome_options)
	driver.get(url)
	time.sleep(4)
	cj= driver.page_source
	#print cj
	#cookie = ''
	#for c in cj:
		#cookie += str(c['name'])+'='+str(c['value'])+';'
	driver.quit()
	return cj

def crawler(tables,dbcons):
	global end
	global dbcon
	dbcon = dbcons
	rowlist = dbcon.table_all_select(tables,'where delay<10')
	for urllist in dbconfig.urllist:
		end = 0
		print str(urllist['name'])+"开始爬取"
		for page in range(1,urllist['page']):
			if '%s' in urllist['url']:
				url = urllist['url']%page
			else:
				url = urllist['url']
			if end == 0:
				t = threading.Thread(target=http_open,args=(url,rowlist,urllist))
				t.start()
			else:
				print("爬取完毕。"+str(urllist['name'])+"大概爬取"+str(page-1)+"页")
				break
			while threading.activeCount() >100:
				time.sleep(3)
			#print("爬取完毕。"+str(urllist['name'])+"大概爬取"+str(page-1)+"页")

			
def http_open(url,rowlist,urllist):
	global end
	while 1:
		heads = dbcon.get_header()
		list = random.choice(rowlist)
		ip = str(list[1])+':'+str(list[2])
		proxy_support = urllib2.ProxyHandler({"https": "https://"+ip})
		opener = urllib2.build_opener(proxy_support)
		urllib2.install_opener(opener)
		for mun in range(2):
			req = urllib2.Request(url,headers=heads)
			try:
				data = urllib2.urlopen(req,timeout = 3)
				break
			except Exception as a:
				try:
					if str(a.getcode()) == '404':
						end = 1
						return
					elif str(a.getcode()) == '503':
						return
					elif str(a.getcode()) == '521':
						print mun
						if mun == 1:
							print '521保护绕过失败。网站地址为->'+str(urllist['name'])
							return
						#heads['Cookie']=COOKIES(url,ip)
						#heads['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
						#try:
						#	data=requests.get(url,headers=heads)
						#	print data
						#except Exception as a:
						#	print a
						data = COOKIES(url,ip)
						#print data
						break
					elif a.getcode() == "Invalid Page":
						return
					else:
						print a.getcode()
						print url
						return
				except:
					return
		break
	dbinstall(data,urllist)

def dbinstall(data,urllist):
	global end
	try:
		coding = (data.info().get("Content-Encoding"))
	except:
		coding = 123
	try:
		if coding == "gzip":
			data = dbcon.gzip1(data.read())
		elif coding == None:
			data =data.read()
		elif coding == 123:
			pass
		else:
			print coding
			print "读取网页信息出现问题"
			return
	except:
		return
	items = re.findall(urllist['regular'],data,re.DOTALL)
 	for list in items:
		pd = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',list[0])
		if pd:
 			ip=pd[0]
		else:
			print pd
 			print "可能网站有恶意注入攻击请注意。"+str(urllist['name'])
 			return
		pd = re.findall('\d{1,5}',list[1])
		if pd:
			port=pd[0]
		else:
			print pd
 			print "可能网站有恶意注入攻击请注意。"+str(urllist['name'])
 			return
 		#print list 
 		if urllist['name'] == 'www.kuaidaili.com' or urllist['name'] == 'www.qydaili.com':
	 		if list[2] in dbconfig.proxytype:
	 			level=dbconfig.proxytype[list[2]]
	 		if list[3] in dbconfig.proxytype:
	 			type=dbconfig.proxytype[list[3]]
	 	elif 'www.xicidaili.com' in urllist['name']:
	 		if list[3] in dbconfig.proxytype:
	 			level=dbconfig.proxytype[list[3]]
	 		if list[4] in dbconfig.proxytype:
	 			type=dbconfig.proxytype[list[4]]
	 	elif urllist['name'] == 'www.89ip.cn' or urllist['name'] == 'www.66ip.cn':
	 		type = 5
	 		level = 5
	 	else:
	 		exit("意外地址请检测")
		data=(ip,port,type)  #可以访问则进行
		row = dbcon.table_select(data,"storage")
		if row[0] == 0:
	 		now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	 		data = (ip,port,type,level,urllist['name'],now_time)
			dbcon.table_install(data,'storage')
			dbcon.table_install(data,'temporary')
		elif row[0] == 1:
			pass
		else:
			dbcon.table_delete(row[1][1][0],'storage')
			print "成功清除重复id"+str(row[1][1][0])
	if not items:
		#print data
		print urllist['url']
		end = 1
if __name__ == "__main__":
	crawler('proxy')



