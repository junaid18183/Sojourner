import os,sys
import time
import sqlite3
import MySQLdb
import json

MYHOME='/home/junedm/Sojourner/'
dbname = MYHOME+'inventory.db'
TIME_FORMAT='%Y-%m-%d %H:%M:%S'

try:
    con=MySQLdb.connect("localhost","root","junedm","sojourner")
    cur=con.cursor()
    #print "DB links established"
except:
    print "DB not accessible"

def log(host, data):

    if type(data) == dict:
	pass

    print "starting %s" %(host)
    facts = data.get('ansible_facts', None)
    now = time.strftime(TIME_FORMAT, time.localtime())
    Hostname = facts.get('ansible_hostname', None)
    Arch = facts.get('ansible_architecture', None)
    Distribution = facts.get('ansible_distribution', None)
    Version = facts.get('ansible_distribution_version', None)
    System = facts.get('ansible_system', None)
    Kernel = facts.get('ansible_kernel', None)
    IPV4 = facts.get('ansible_default_ipv4', None).get('address', None)
    #IPV4 = facts.get('ansible_eth0', None).get('ipv4', None).get('address', None)

    print now,Hostname,Arch,Distribution,Version,System,Kernel,IPV4

    try:
        # `host` is a unique index
        query="""REPLACE INTO facts (Last_Update,Hostname,Arch,Distribution,Version,System,Kernel,Eth0_ip) VALUES('%s','%s','%s','%s','%s','%s','%s','%s');""" %(
 	now,Hostname,Arch,Distribution,Version,System,Kernel,IPV4)
	
	cur.execute(query)
	query="""REPLACE INTO inventory (Hostname) VALUES('%s');""" %(Hostname)
	cur.execute(query)
        con.commit()
	print "%s done" %(host)
#    except:
    except MySQLdb.Error as err:
        print("Something went wrong: {}".format(err))
        #pass
 	print "My name is %s" %(host)

#--For all
path = "/tmp/facts/"
hostlist=os.listdir( path )
for file in hostlist:
	if os.path.isfile(path+file):
		json_data = open(path+file)
		data = json.load(json_data)
		log(file, data)
		#os.rename(path+file,path+"done/"+file)

#--single host

#json_data = open('/tmp/facts/ggvaapp07')
#data = json.load(json_data)
#log(file, data)
