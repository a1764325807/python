#!-*- coding=utf-8 -*-
from text import *
import sys
sys.path.append("..")
from crawler.crawler import *

print("+++++++++++++++++++++++++++++++++++\n开始验证proxy表中的数据")
#kong('proxy')
print("+++++++++++++++++++++++++++++++++++\n开始爬虫进程")
crawler('proxy')
print("+++++++++++++++++++++++++++++++++++\n开始测试temporary中的数据")
kong('temporary')
print("+++++++++++++++++++++++++++++++++++\n开始验证recycle表中的数据")
kong('recycle')





