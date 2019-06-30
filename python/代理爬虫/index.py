#!-*- coding=utf-8 -*-
from db.dborder import *
import db.dbconfig
dbcon = mysqlconnect()


print dbconfig.get_header()
"""
#查找实例 ip port
data=('46.52.153.74','38724','1')
tables="proxy"# or "recycle"
data =dbcon.table_select(data,tables)
print data[1][0][0]
"""
"""
#删除实例 id
data=('2')
tables="proxy" or "recycle"
dbcon.table_delete(data,tables)
"""
"""
#修改实例 key values id
data = ('time','1314','3')
tables="proxy" or "recycle"
dbcon.table_update(data,tables)
"""
"""
#插入实例 ip port score time
data = ('123.123.123.123',369,2,'44.12')
tables="proxy" or "recycle"
dbcon.table_install(data,tables)
"""




