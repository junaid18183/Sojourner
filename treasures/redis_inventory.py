import json,redis,os

TIME_FORMAT='%Y-%m-%d %H:%M:%S'
########################################################################################
FACT_EXPIRATION = 86400

redis = redis.Redis()

def log(host, data):
    if type(data) == dict:
    	facts = data.get('ansible_facts', None)

    redis_pipe = redis.pipeline()
    for fact in facts:
        # Only store the basic types (strings) of facts
        #if isinstance(facts[fact], basestring):
        redis_pipe.hset(host, fact, facts[fact])
    redis_pipe.expire(host, FACT_EXPIRATION)
    redis_pipe.execute()
######################################################################################

#--For all
path = "/tmp/facts/"
hostlist=os.listdir( path )
for file in hostlist:
	if os.path.isfile(path+file):
		json_data = open(path+file)
		data = json.load(json_data)
		log(file, data)
		#os.rename(path+file,path+"done/"+file)

