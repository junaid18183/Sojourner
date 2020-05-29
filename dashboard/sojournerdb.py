#!/usr/local/bin/python

from mk_livestatus import Socket
import json,subprocess,re,time,collections,sys,pymongo,os,datetime
from pymongo import MongoClient
import time

mongoserver = "localhost"
mongoport = 27017
mydb = "sojourner"
#mydb = "inventory"
collection_name = "sojourner"
#collection_name = "inventory"
#mycollections = {'ansible':"ansible",'check_mk':"cmk",'inventory':"inventory"}
basedir = '/home/karang'
cmkdict = collections.defaultdict(dict)
ansibledict = collections.defaultdict(dict)
inventorydict = collections.defaultdict(dict)
opdict = collections.defaultdict(dict)

mydc = {'colo':["nagios.glam.colo","/omd/sites/nagiosmon1/tmp/run/live"],'ggva':["nagios.ggva.glam.colo","/omd/sites/ggva_nagios/tmp/run/live"]}


def get_cmknewdata(host,dc):
	#q = s.hosts.columns('name', 'custom_variable_values','contact_groups','contacts').filter('host_name = cscpapp73vm2')
	if dc == "colo" or dc == "ggva" and host != "":
		s=Socket(mydc[dc][1])
		s=Socket((mydc[dc][0],6557))
		if host != "all":
			query = s.hosts.columns('name', 'custom_variable_values','contact_groups','contacts','state').filter('host_name = '+ host)
			querycmk(s,query)
		elif host == "all":
			query = s.hosts.columns('name', 'custom_variable_values','contact_groups','contacts','state')
			querycmk(s,query)	
		else:
			print "Wrong host"
	elif dc == "all":
		for dc in mydc:
			s=Socket(mydc[dc][1])
			s=Socket((mydc[dc][0],6557))
			query = s.hosts.columns('name', 'custom_variable_values','contact_groups','contacts','state')
			querycmk(s,query)	
	else:
		print "wrong dc"		

def querycmk(socket,query):
		result = query.call()
		data_string = json.dumps(result)

		# For decoding change the JSON string into a JSON object
		jsonObject = json.loads(data_string)
		for data in jsonObject:
			JSONString = json.dumps(data)
			JSONDict = json.loads(JSONString)
			#Get name of host from JsonString
			host_name = JSONDict['name']
			#Get Tags from JsonString
			tags = JSONDict['custom_variable_values']
			contacts = JSONDict['contacts']
			if "slack" in contacts and "check_mk" in contacts:
				contacts = re.sub(r'(slack,|check_mk,)','',contacts)
			contact_groups = JSONDict['contact_groups']
			if "check_mk" in contact_groups:
				contact_groups = re.sub(r'(slack,|,check_mk|check_mk,)','',contact_groups)
			state = JSONDict['state']
			cmkdict = parse_data(tags,host_name,contacts,contact_groups,state)

def parseFacts():
	print 'gathering ansible facts'
	time.sleep(1)
	for dc in mydc:
		mydir = os.path.join(basedir, dc)
		if os.path.exists(mydir):
			factfiles = os.listdir(os.path.join(basedir, dc))
			for myfile in factfiles:
				with open(os.path.join(mydir, myfile)) as fh:
					jsondata = json.load(fh)
					if not jsondata.has_key('ansible_facts'):
						print 'warning: %s incorrect facts file, skipping' % myfile
						time.sleep(0.2)
						continue
					if myfile != jsondata['ansible_facts']['ansible_hostname']:
						myfile = jsondata['ansible_facts']['ansible_hostname']
					#ansibledict[myfile]['host_name'] = jsondata['ansible_facts']['ansible_hostname']
					templist = list()
					ansibledict[myfile]['network'] = {}
					for interface in jsondata['ansible_facts']['ansible_interfaces']:
						if re.search(r'((eth\d)(([.]\d+)?)$)', interface) or re.search(r'((bond\d)(([.]\d+)?)$)', interface) or\
							re.search(r'lxc\d', interface) or re.search(r'xen\d', interface):
							ansibledict[myfile]['network'][interface] = {'ipv4': '', 'mac': ''}
							mykey = 'ansible_' + interface
							if jsondata['ansible_facts'][mykey].has_key('ipv4'):
								ansibledict[myfile]['network'][interface]['ipv4'] = jsondata['ansible_facts'][mykey]['ipv4']\
									['address']
								templist.append(jsondata['ansible_facts'][mykey]['ipv4']['address'])
							if jsondata['ansible_facts'][mykey].has_key('macaddress'):
								ansibledict[myfile]['network'][interface]['mac'] = jsondata['ansible_facts'][mykey]['macaddress']
					viplist=list()
					for ipaddr in jsondata['ansible_facts']['ansible_all_ipv4_addresses']:
						if ipaddr not in templist:
							viplist.append(ipaddr)
					ansibledict[myfile]['network']['vip'] = viplist
					if not jsondata['ansible_facts'].has_key('ansible_local'):
						ansibledict[myfile]['asset_id'] = ''
						ansibledict[myfile]['crid'] = ''
						ansibledict[myfile]['rack'] = ''
						print 'warning: %s local facts not found, set empty' % myfile
						time.sleep(0.2)
					else:
						if jsondata['ansible_facts']['ansible_local'].has_key('sojourner'):
							if jsondata['ansible_facts']['ansible_local']['sojourner'].has_key('inventory'):
								ansibledict[myfile]['asset_id'] = jsondata['ansible_facts']['ansible_local']['sojourner']\
																	['inventory']['asset_tag']
								ansibledict[myfile]['crid'] = jsondata['ansible_facts']['ansible_local']['sojourner']['inventory']\
																['crid']
								ansibledict[myfile]['rack'] = jsondata['ansible_facts']['ansible_local']['sojourner']['inventory']\
																['rack']
							else:
								ansibledict[myfile]['asset_id'] = ''
								ansibledict[myfile]['crid'] = ''
								ansibledict[myfile]['rack'] = ''
								print 'warning: %s local facts not found, set empty' % myfile
								time.sleep(0.2)
						else:
							ansibledict[myfile]['asset_id'] = ''
							ansibledict[myfile]['crid'] = ''
							ansibledict[myfile]['rack'] = ''
							print 'warning: %s local facts not found, set empty' % myfile
							time.sleep(0.2)
					ansibledict[myfile]['model'] = jsondata['ansible_facts']['ansible_system_vendor'] + ' ' + \
													   jsondata['ansible_facts']['ansible_product_name']
					ansibledict[myfile]['ncpu'] = str(jsondata['ansible_facts']['ansible_processor_vcpus'])
					ansibledict[myfile]['mem'] = str(jsondata['ansible_facts']['ansible_memtotal_mb'])
					ansibledict[myfile]['os'] = jsondata['ansible_facts']['ansible_distribution']
					ansibledict[myfile]['os_ver'] = jsondata['ansible_facts']['ansible_distribution_version']
					ansibledict[myfile]['disk'] = collections.defaultdict(dict)
					for device in jsondata['ansible_facts']['ansible_devices']:
						ansibledict[myfile]['disk']['raw'][device] = jsondata['ansible_facts']['ansible_devices'][device]['size']
					for mount in jsondata['ansible_facts']['ansible_mounts']:
						if not re.search(r'/proc', mount['device']):
							ansibledict[myfile]['disk']['mount'][mount['device']] = mount['mount']
					interdict = dict(ansibledict[myfile]['disk'])
					ansibledict[myfile]['disk'] = interdict
					if re.search(r'vm\d+', jsondata['ansible_facts']['ansible_hostname']) or jsondata['ansible_facts']\
																				['ansible_virtualization_type'] != 'NA':
						ansibledict[myfile]['virt'] = 'Y'
					else:
						ansibledict[myfile]['virt'] = 'N'
					ansibledict[myfile]['last_update'] = jsondata['ansible_facts']['ansible_date_time']['date'] + ' ' + \
															jsondata['ansible_facts']['ansible_date_time']['time']
					ansibledict[myfile]['_id'] = jsondata['ansible_facts']['ansible_hostname']
		

def parse_data(tags,host_name,contacts,contact_groups,state):
	only_role = re.sub(r'^.*,',"",tags)
	final_tags = re.sub(r' PROD',"",only_role)
	#Check for DC
	list_tags = []
	list_tags = re.sub(r'^(.+?),','',tags)

	if list_tags:
		for i in list_tags:
			length = len(list_tags.split(" "))
			if length < 1:
				DC = ''
			else:
				DC = list_tags.split(" ")[0]

			if length < 2:
				env = ''
			else:
				env = list_tags.split(" ")[1]

			if length < 3:
				product = ''
			else:
				product = list_tags.split(" ")[2]

			role = []
			if length > 2:
				for i in range(3, length):
					role.append(list_tags.split(" ")[i])
			else:
				role = [] 

		cmkdict[host_name]['_id'] = host_name
		cmkdict[host_name]['dc'] = DC
		cmkdict[host_name]['environment'] = env
		cmkdict[host_name]['product'] = product
		cmkdict[host_name]['role'] = role
		cmkdict[host_name]['contacts'] = contacts
		cmkdict[host_name]['contact_groups'] = contact_groups
		cmkdict[host_name]['last_update_cmk'] = time.strftime("%Y-%m-%d %H:%M:%S")
		if (state == "0"):
			state = "UP"
			cmkdict[host_name]['state'] = state
		else:
			state = "DOWN"
			cmkdict[host_name]['state'] = state
	else:
		print "%s tags not defined" %host_name
	return cmkdict


def dumpDB(commondict,mycollection):

	try:
		conn = pymongo.MongoClient(mongoserver,mongoport)
	except pymongo.errors.ConnectionFailure, e:
		print "Could not connect to MongoDB: %s" % e

	db = conn[mydb]
	collection = db[mycollection]
	count = 0
	for host in commondict.keys():
		try:
			collection.insert(commondict[host], check_keys=False)
			print '%s: complete document insert done' % host
			count = count + 1
		except pymongo.errors.DuplicateKeyError:
			if cmp(collection.find_one({'_id': host}), commondict[host]) is not 0:
				partial = list()
				for key in commondict[host].keys():
					dbcoll = collection.find_one({'_id': host})
					if key not in dbcoll:
						collection.update({'_id': host}, {'$set': {key: commondict[host][key]}}, check_keys=False) 
						partial.append(key)
						count = count + 1
					elif commondict[host][key] != collection.find_one({'_id': host})[key]:
						collection.update({'_id': host}, {'$set': {key: commondict[host][key]}}, upsert = False)
						partial.append(key)
						count = count + 1
	#if count != 0:
	#	print 'database changed: %d document updated' % count
	#else:
	#	print ""
	#	print 'database not changed'		

def mergeDB():
	print "Merging check_mk and ansible data"
	for host_name in cmkdict.keys():
		inventorydict[host_name] = ansibledict[host_name]
		inventorydict[host_name].update(cmkdict[host_name])

def parse_userquery(host,finalargs):
	if host != "all":
		if re.search(r'^app*',host) or re.search(r'^cs*',host) or re.search(r'^rsca*',host) or re.search(r'^ammon*',host) or re.search(r'^ggcs*',host):
			#Passing query to get_cmkdata method
			get_cmknewdata(host,"colo")
			#Dumping the data for that query
			dumpDB(cmkdict,collection_name)
			#Get data from DB
			op=get_dbdata(host,finalargs)
		elif re.search(r'^ggva*',host):	
			#Passing query to get_cmkdata method
			get_cmknewdata(host,"ggva")
			#Dumping the data for that query
			dumpDB(cmkdict,collection_name)
			#Get data from DB
			op=get_dbdata(host,finalargs)
		else:
			#Query for all hosts
			get_cmknewdata(host,"all")
			#Dumping the data for that query
			dumpDB(cmkdict,collection_name)
			#Get data from DB
			op=get_dbdata(host,finalargs)
	else:
		if "dc" in finalargs:
			for key in finalargs:
				if key == "dc":
					dc = finalargs[key]
			if dc.upper() == "COLO":
				get_cmknewdata(host,"colo")
				#Dumping the data for that query
				dumpDB(cmkdict,collection_name)
				#Get data from DB
				op=get_dbdata(host,finalargs)

			elif dc.upper() == "GGVA":
				get_cmknewdata(host,"ggva")
				#Dumping the data for that query
				dumpDB(cmkdict,collection_name)
				#Get data from DB
				op=get_dbdata(host,finalargs)
			else:
				print "Wrond DC"
				exit()
		else:
			#Query for all hosts		
			get_cmknewdata(host,"all")
			#Dumping the data for that query
			dumpDB(cmkdict,collection_name)
			#Get data from DB
			op=get_dbdata(host,finalargs)
	return op

def get_dbdata(host,finalargs):
	try:
		conn = pymongo.MongoClient(mongoserver,mongoport)
	except pymongo.errors.ConnectionFailure, e:
		print "Could not connect to MongoDB: %s" % e

	db = conn[mydb]
	collname = collection_name 
	collection = db[collname]
	if host != "all":
		op = collection.find_one({'_id': host})
		count = collection.find({'_id':host}).count()
	else:
		if finalargs:
			if collection.find(finalargs).count() > 0:
				op = collection.find(finalargs)	
				count = collection.find(finalargs).count()
			else:
				print "Wrong option provided\n"
				print "Please run 'sojourner list --help' for list of products and roles\n"
				exit ()
		else:
			op = collection.find()
			count = collection.find().count()
	return op,count

def get_uniquevaluesdb(arg):
	try:
		conn = pymongo.MongoClient(mongoserver,mongoport)
	except pymongo.errors.ConnectionFailure, e:
		print "Could not connect to MongoDB: %s" % e

	db = conn[mydb]
	collname = collection_name
	collection = db[collname]

	if arg != "column":	
		op = collection.distinct(arg)
	else:	
		op = collection.find_one()
	
	return op

def dumpall():
	get_cmknewdata("all","all")
	dumpDB(cmkdict,collection_name)

if __name__ == '__main__':
	dumpall()	
