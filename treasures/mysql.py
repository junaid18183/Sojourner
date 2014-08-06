#!/usr/bin/python
#yum install MySQL-python.x86_64
import MySQLdb
import csv
db=MySQLdb.connect("localhost","root","junedm","sojourner")
cursor=db.cursor()
#cursor.execute("select * from inventory");
#result=cursor.fetchall()
#print result


csv_data = csv.reader(file('invnetory.csv'))
for row in csv_data:
	query="""insert into inventory values ('%s',%s,'%s','%s','%s','%s','%s');""" %(row[2],row[1],row[3],row[6],row[7],row[8],row[9])
	#cursor.execute(query)
	#result=cursor.fetchall()
	#print result
	print query

