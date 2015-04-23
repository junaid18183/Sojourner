#!/usr/bin/env python

import json
import redis
import sys

from list_to_table import format_as_table

mykeys=['ansible_hostname', 'ansible_distribution','ansible_kernel']

data=[]

r = redis.Redis()
for key in r.keys():
	facts = r.hgetall(key)
	data.append(map(facts.get, mykeys))
	#print type(facts)
	#print facts.get('ansible_local').get('sojourner').get('Role')
	
print data

######################################################################
header = ['Name', 'OS', 'Kernel', 'sojourner']
sort_by_key = 'ansible_hostname'
sort_order_reverse = True
#print format_as_table(data,mykeys,header,sort_by_key,sort_order_reverse)

######################################################################
for key in r.keys():
	for name in mykeys :
		#print r.hmget(key,name)
		print "commented"
######################################################################
mykeys=['ansible_hostname', 'ansible_distribution','ansible_kernel', 'ansible_local']
r = redis.Redis()
for key in r.keys():
	a=r.hmget(key,mykeys)
	print a,type(a)
	print type(a[3])

