#!/usr/bin/python
#yum install MySQL-python.x86_64
import MySQLdb
import csv
db=MySQLdb.connect("localhost","root","junedm","sojourner")
cursor=db.cursor()
#cursor.execute("select * from inventory");
#result=cursor.fetchall()
#print result


csv_data = csv.reader(file('colo1.csv'))
for row in csv_data:
	query="""insert into inventory values ('%s',%s,'%s','%s','%s','%s','%s');""" %(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
	cursor.execute(query)
	result=cursor.fetchall()
	print result
	#print query

