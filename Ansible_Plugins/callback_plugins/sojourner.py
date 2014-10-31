import os,time
from ConfigParser import SafeConfigParser
# +----------------------------------------------------------------------+
#Variables
TIME_FORMAT='%Y-%m-%d %H:%M:%S'
# +----------------------------------------------------------------------+
#Variables
parser = SafeConfigParser()
parser.read('/plugins_scripts/Git_repos/Sojourner/conf/sojourner.conf')
SOUJOURNER_HOME=parser.get('sojourner', 'SOUJOURNER_HOME')
# +----------------------------------------------------------------------+
class DatabaseConnection( object ):
    def __init__( self ):
        db_engine=parser.get('sojourner', 'db_engine')
        if db_engine == 'mysql':
                import MySQLdb

                self.conn   = None
                self.cursor = None

                self.host   = parser.get("sojourner","host")
                self.user   = parser.get("sojourner","user")
                self.passwd = parser.get("sojourner","passwd")
                self.db     = parser.get("sojourner","dbname")
                self.conn   = MySQLdb.Connect(self.host,self.user,self.passwd,self.db)
                self.cursor = self.conn.cursor ( MySQLdb.cursors.DictCursor )

        elif db_engine == 'sqlite':
                import sqlite3
                self.db=parser.get('sojourner', 'dbname')
                self.db = SOUJOURNER_HOME+'data_base/'+self.db+'.db'
                self.conn = sqlite3.connect(self.db)
                self.conn.row_factory=sqlite3.Row
                self.cursor = self.conn.cursor()
        else :
                print "The db_engine should be mysql or sqlite only, you entered %s" %db_engine
                exit(1)


    def __del__( self ):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
	    self.conn.commit()
            self.conn.close()
# +----------------------------------------------------------------------+
def log(host, data):
	try:
    		conn = DatabaseConnection()
    		cursor = conn.cursor

	except:
    		#pass
    		print "Teri Maa ki tang"


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
		#print query
		cursor.execute(query)
		#print cursor.rowcount

		query="""REPLACE INTO inventory (Hostname,Crid,Product,Role) VALUES('%s',%s,'%s','%s');""" %(Hostname,Crid,Product,Role)
		#print query
        	cursor.execute(query)
		affected_records=cursor.rowcount
		#print affected_records

	except:
 		print "Not able to run sojourner callback-plugin"

# +----------------------------------------------------------------------+
class CallbackModule(object):
    def runner_on_ok(self, host, res):
        log(host, res)
