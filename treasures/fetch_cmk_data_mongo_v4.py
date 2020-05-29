#!/usr/local/bin/python

# This program gets data from check_mk server using LQL query and dump the data in database
#Author: huzefah@glam.com

from mk_livestatus import Socket
import json,subprocess,re,time,collections,sys,pymongo
import argparse


mongoserver = "tiber"
mongoport = 27017
mydb = "inventory"
cmkcollection = "cmk"
#nagios_server = "app217.glam.colo"
#socket_path = "/omd/sites/nagiosmon1/tmp/run/live"
#s=Socket(socket_path)
#s=Socket((nagios_server,6557))
cmkdist = collections.defaultdict(dict)


#cmkdist = {}

mydc = {'colo':["nagios.glam.colo","/omd/sites/nagiosmon1/tmp/run/live"],'ggva':["nagios.ggva.glam.colo","/omd/sites/ggva_nagios/tmp/run/live"],'scl':["nagios.scl.glam.colo","/omd/sites/glam_ning/tmp/run/live"]}
mydb = 'inventory'
mytable = 'cmk'
myengine = 'InnoDB'



def get_data():
	for dc in mydc:
		#print dc, mydc[dc][0], mydc[dc][1] 
		s=Socket(mydc[dc][1])
		s=Socket((mydc[dc][0],6557))
		#q = s.hosts.columns('name', 'custom_variable_values','contact_groups','contacts').filter('host_name = cscpapp73vm2')
		#q = s.hosts.columns('name','state').filter('host_name = ggvahdp12')
		q = s.hosts.columns('name', 'custom_variable_values','contact_groups','contacts','state')
		result = q.call()
		data_string = json.dumps(result)

		# For decoding change the JSON string into a JSON object
		jsonObject = json.loads(data_string)

		for data in jsonObject:
			JSONString = json.dumps(data)
			#print "string=",JSONString
			JSONDict = json.loads(JSONString)
			#Get name of host from JsonString
			host_name = JSONDict['name']
			#Get Tags from JsonString
			tags = JSONDict['custom_variable_values']
			contacts = JSONDict['contacts']
			contact_groups = JSONDict['contact_groups']
			state = JSONDict['state']
			cmkdist = parse_data(tags,host_name,contacts,contact_groups,state)

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
				role = '' 
		
		#print "host_name={} DC={} env={} product={} role={}".format(host_name,DC,env,product,role)
		cmkdist[host_name]['_id'] = host_name
		cmkdist[host_name]['dc'] = DC 
		cmkdist[host_name]['environment'] = env
		cmkdist[host_name]['product'] = product
		cmkdist[host_name]['role'] = role
		cmkdist[host_name]['contacts'] = contacts
		cmkdist[host_name]['contact_groups'] = contact_groups
		if (state == "0"):
			state = "UP"
			cmkdist[host_name]['state'] = state
		else:
			state = "DOWN"
			cmkdist[host_name]['state'] = state
	else:
		print "%s tags not defined" %host_name
	return cmkdist	


def dumpDB_Mongo(cmkdist):
	print "Dumping data into MongoDB"
	
	try:	
		conn = pymongo.MongoClient(mongoserver,mongoport)
		print "Connected to MongoDB successfully"
	except pymongo.errors.ConnectionFailure, e:
		print "Could not connect to MongoDB: %s" % e 

	db = conn[mydb]
	collection = db[cmkcollection]
	count = 0	
	for host in cmkdist:
		try:
			collection.insert(cmkdist[host],check_keys=False)	
			print "Document added successfully in Mongo DB"
				
		except pymongo.errors.DuplicateKeyError:
			if cmp(collection.find_one({'_id': host}), cmkdist[host]) is not 0:
				collection.update({'_id': host}, {'$set': cmkdist[host]}, upsert = True)
				print host + ' document updated'
				for key in cmkdist[host][key] != collection.find_one({'_id': host})[key]:
					collection.update({'_id': host}, {'$set': {key: cmkdist[host][key]}}, upsert = True)
					partial.append(key)
					count = count + 1
					print '%s: partial document insert done. [%s]' % (host, ', '.join(partial))
	if count != 0:
		print 'collection changed: %d document updated' % count
	else:
		print '%s: collection not changed' % cmkcollection


get_data()
dumpDB_Mongo(cmkdist)
