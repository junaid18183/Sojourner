# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import os
import sojourner.utils.constants as C

from prettytable import PrettyTable #https://code.google.com/p/prettytable/wiki/Tutorial
from prettytable import from_db_cursor

# +----------------------------------------------------------------------+
class DatabaseConnection( object ):
    def __init__( self ):
        db_engine=C.DEFAULT_DB_ENGINE
        if db_engine == 'mysql':
                import MySQLdb

                self.conn   = None
                self.cursor = None

                self.host   = C.DEFAULT_DB_HOST 
                self.user   = C.DEFAULT_DB_USER
                self.passwd = C.DEFAULT_DB_PASSWD
                self.db     = C.DEFAULT_DB_DBNAME  
	  	self.port   = int(C.DEFAULT_DB_PORT)
                self.conn   = MySQLdb.Connect(self.host,self.user,self.passwd,self.db,self.port)
                #self.cursor = self.conn.cursor ( MySQLdb.cursors.DictCursor ) # with this mysql columns were also visible
                self.cursor = self.conn.cursor()

        else :
                db_engine = 'sqlite' # By default we use sqlite
                import sqlite3
                #self.db = str(C.DEFAULT_SOJOURNER_HOME + 'data_base/' + C.DEFAULT_DB_DBNAME + '.db')
 		# Now Decided that we will be using hardcoded path for the sqlite database
		self.db = '/var/lib/sojourner/sojourner.db'
		if os.path.isfile(self.db):
			#check if first 100 bytes of path identifies itself as sqlite3 in header
			f = open('/var/lib/sojourner/sojourner.db', "rx")
    			ima = f.read(16).encode('hex')
    			f.close()
    			#see http://www.sqlite.org/fileformat.html#database_header magic header string
    			if ima != "53514c69746520666f726d6174203300": 
				print ("sojourner database corrupted,Re-creating the fresh Database.")
        			create_sqlite_db()
		else:
			create_sqlite_db()
                self.conn = sqlite3.connect(self.db)
                self.conn.row_factory=sqlite3.Row
                self.cursor = self.conn.cursor()

    def __del__( self ):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
# +----------------------------------------------------------------------+
def create_sqlite_db():
	import sqlite3
	path="/var/lib/sojourner/"
	db = path + 'sojourner.db'
	os.mkdir(path)
	conn = sqlite3.connect(db)
	sql = '''CREATE TABLE IF NOT EXISTS facts (Last_Update DATE,Hostname TEXT PRIMARY KEY,
						   Arch TEXT , 
 						   Distribution TEXT , 
						   Version TEXT , 
						   System TEXT, 
						   Kernel TEXT, 
					   	Eth0_ip TEXT
					   	);'''
	conn.execute(sql)

	sql = '''CREATE TABLE IF NOT EXISTS inventory ( Hostname TEXT PRIMARY KEY , 
						Crid INTEGER , 
						Asset_ID TEXT, 
						Price TEXT, 
						Role TEXT, 
						Product TEXT, 
						Owner TEXT ,
						DC TEXT 
						);'''

	conn.execute(sql)
	conn.commit()
	conn.close()
# +----------------------------------------------------------------------+
def execute_sql(sql,raw=False) :
        conn = DatabaseConnection()
        cursor = conn.cursor
        cursor.execute(sql)
        affected_records=cursor.rowcount

        if not raw:
                pt = from_db_cursor(cursor,print_empty=True)
        else:
                pt = cursor.fetchall()
        return pt,affected_records
# +----------------------------------------------------------------------+
