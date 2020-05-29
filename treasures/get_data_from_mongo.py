
from mk_livestatus import Socket
import json,subprocess,re,time,collections,sys,pymongo,os,datetime
from pymongo import MongoClient

mongoserver = "app161vm4.glam.colo"
mongoport = 27017
mydb = "inventory"

mycollections = {'ansible':"ansible",'check_mk':"cmk",'inventory':"inventory"}
cmkdict = collections.defaultdict(dict)
ansibledict = collections.defaultdict(dict)
inventorydict = collections.defaultdict(dict)
opdict = collections.defaultdict(dict)

mydc = {'colo':["nagios.glam.colo","/omd/sites/nagiosmon1/tmp/run/live"],'ggva':["nagios.ggva.glam.colo","/omd/sites/ggva_nagios/tmp/run/live"],'scl':["nagios.scl.glam.colo","/omd/sites/glam_ning/tmp/run/live"]}


#pip install python-mk-livestatus
#pip install pymongo
#import inventorydb_v4
import sys

def get_dbdata(host):
        try:
                conn = pymongo.MongoClient(mongoserver,mongoport)
                print "Connected to MongoDB successfully"
        except pymongo.errors.ConnectionFailure, e:
                print "Could not connect to MongoDB: %s" % e

        db = conn[mydb]
        collname = "inventory"
        collection = db[collname]
        op = collection.find_one({'_id': host})
        #count = collection.find({'_id':host}).count()
        return op



op=get_dbdata(sys.argv[1])
print op
print type(op)
