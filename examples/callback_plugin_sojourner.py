import os,time
import sys

from sojourner.utils.dbcon import execute_sql

# +----------------------------------------------------------------------+
#Variables
TIME_FORMAT='%Y-%m-%d %H:%M:%S'

# +----------------------------------------------------------------------+
def log(host, data):
	if type(data) == dict:
        	invocation = data.pop('invocation', None)
        	if invocation.get('module_name', None) != 'setup':
            		return

	facts = data.get('ansible_facts', None)
	now = time.strftime(TIME_FORMAT, time.localtime())
	Hostname = facts.get('ansible_hostname', None)
	Arch = facts.get('ansible_architecture', None)
	Distribution = facts.get('ansible_distribution', None)
	Version = facts.get('ansible_distribution_version', None)
	System = facts.get('ansible_system', None)
	Kernel = facts.get('ansible_kernel', None)
	IPV4 = facts.get('ansible_default_ipv4', None).get('address', None)
	#IPV4 = facts.get('ansible_default_ipv4', None).get('address', None), Since I am working on Vagrant eth0 is always 10.0.2.15
	Crid = 786 # temp fix
	ansible_local=facts.get('ansible_local',None)
	if ansible_local:
		Product = facts.get('ansible_local',None).get('sojourner',None).get('Product',None)
		Role = facts.get('ansible_local',None).get('sojourner',None).get('Role',None)
	else:
		Product = None
		Role = None

	try:
		query="""REPLACE INTO facts (Last_Update,Hostname,Arch,Distribution,Version,System,Kernel,Eth0_ip) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');""" %(now,Hostname,Arch,Distribution,Version,System,Kernel,IPV4)
		#print (query)		
		data=execute_sql(query)[0]
		#print (data)

		query="""REPLACE INTO inventory (Hostname,Crid,Product,Role) VALUES('%s',%s,'%s','%s');""" %(Hostname,Crid,Product,Role)
        	
		affected_records=execute_sql(query)[0]
		#print affected_records

	except:
 		print "Not able to run sojourner callback-plugin"

# +----------------------------------------------------------------------+
class CallbackModule(object):
    def runner_on_ok(self, host, res):
        log(host, res)
