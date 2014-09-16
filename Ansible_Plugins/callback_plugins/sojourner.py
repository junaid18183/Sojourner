import os,time,sqlite3
# +----------------------------------------------------------------------+
#Variables

SOUJOURNER_HOME='/home/junedm/Sojourner/'
dbname = SOUJOURNER_HOME+'inventory.db'
TIME_FORMAT='%Y-%m-%d %H:%M:%S'
# +----------------------------------------------------------------------+

try:
    con = sqlite3.connect(dbname)
    cur = con.cursor()
except:
    pass

def log(host, data):

    if type(data) == dict:
        invocation = data.pop('invocation', None)
        if invocation.get('module_name', None) != 'setup':
            return

    facts = data.get('ansible_facts', None)

    now = time.strftime(TIME_FORMAT, time.localtime())

    try:
        # `host` is a unique index
        cur.execute("REPLACE INTO ans_facts (Last_Update,Hostname,Arch,Distribution,Version,System,Kernel,Eth0_ip,Product,Role) VALUES(?,?,?,?,?,?,?,?,?,?);",
        (
            now,
            facts.get('ansible_hostname', None),
            facts.get('ansible_architecture', None),
            facts.get('ansible_distribution', None),
            facts.get('ansible_distribution_version', None),
            facts.get('ansible_system', None),
            facts.get('ansible_kernel', None),
	    facts.get('ansible_eth0', None).get('ipv4', None).get('address', None),
	    facts.get('ansible_local', None).get('sojourner', None).get('Product', None),
	    facts.get('ansible_local', None).get('sojourner', None).get('Role', None),
        ))
        con.commit()
    except:
        #pass
 	print "Not able to run sojourner plugin"

class CallbackModule(object):
    def runner_on_ok(self, host, res):
        log(host, res)
