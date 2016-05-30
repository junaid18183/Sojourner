#!/usr/bin/python
#
# inventory.py callback. Create and update couchdb database entries.
# With a bit of DNA from from Jan-Piet Mens' excellent work at
# http://jpmens.net/2012/09/11/watching-ansible-at-work-callbacks/
# (which is oriented to sqlite3)
#
# This goes in /usr/lib/python[version]/site-packages/ansible/callback_plugins
 
import time,os,json
import couchdb
import hashlib
 
couch_server = '10.143.0.29'
 
TIME_FORMAT='%Y-%m-%d %H:%M:%S'
couch = couchdb.Server('http://' + couch_server + ':5984/')
db = couch['sojourner']
 
def log(host, data):
 
    #if type(data) == dict:
    #    invocation = data.pop('invocation', None)
    #    if invocation.get('module_name', None) != 'setup':
    #        return
 
    facts = data.get('ansible_facts', None)
 
    now = time.strftime(TIME_FORMAT, time.localtime())
 
    # We use a hash of hostname and mac address on the primary interface for a unique ID
    #m = hashlib.md5(facts['ansible_hostname'] + facts['ansible_default_ipv4']['macaddress'])
    #id = m.hexdigest()
    id = facts['ansible_hostname']
 
    # Note that we don't check for conflicts here.
    try:
        if id in db:
            doc = db[id]
        else:
            doc = {'_id': id}
 
        doc['updated'] = now
        #doc['ansible_facts'] = facts
	for key, value in facts.iteritems():
		doc[key]=value
        db.save(doc)
    except:
        raise
######################################################################################################### 
#--For all
path = "/tmp/facts/"
hostlist=os.listdir( path )
for file in hostlist:
        if os.path.isfile(path+file):
                json_data = open(path+file)
                data = json.load(json_data)
                log(file, data)
                #os.rename(path+file,path+"done/"+file)

