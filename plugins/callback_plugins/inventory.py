import os
import time
import sqlite3
import MySQLdb


MYHOME='/home/junedm/Sojourner/'
dbname = MYHOME+'inventory.db'
TIME_FORMAT='%Y-%m-%d %H:%M:%S'

try:
    #con = sqlite3.connect(dbname)
    #cur = con.cursor()
    db=MySQLdb.connect("localhost","root","junedm","sojourner")
    cur=db.cursor()
except:
    pass

def log(host, data):

    if type(data) == dict:
        invocation = data.pop('invocation', None)
        if invocation.get('module_name', None) != 'setup':
            return

    facts = data.get('ansible_facts', None)
    print type(facts)

    now = time.strftime(TIME_FORMAT, time.localtime())

    try:
        # `host` is a unique index
        cur.execute("""REPLACE INTO facts (Last_Update,Hostname,Arch,Distribution,Version,System,Kernel,Eth0_ip) VALUES('%s','%s','%s','%s','%s','%s','%s','%s');""" %
        (
            now,
            facts.get('ansible_hostname', None),
            facts.get('ansible_architecture', None),
            facts.get('ansible_distribution', None),
            facts.get('ansible_distribution_version', None),
            facts.get('ansible_system', None),
            facts.get('ansible_kernel', None),
	    facts.get('ansible_eth0', None).get('ipv4', None).get('address', None),
        ))
        con.commit()
    except:
        #pass
 	print "My name is Khan"

class CallbackModule(object):
    def runner_on_ok(self, host, res):
        log(host, res)
