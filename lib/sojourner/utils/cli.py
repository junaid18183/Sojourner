# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

#In Python 3, the keyword print has been changed from calling a statement to calling a function.
#So instead of saying print value you now need to say print(value), or you'll get a SyntaxError.

__metaclass__ = type

import re,argparse,os,sys
#import commands #Not using commands
from subprocess import Popen, PIPE

from sojourner.utils.dbcon import *

try:
    import json
except ImportError:
    import simplejson as json
# +----------------------------------------------------------------------+
# This is for ansible inventory
def grouplist():

        inventory ={}
        # Add group for [local] (e.g. local_action). If needed,
        # set ansible_python_interpreter in host_vars/127.0.0.1
        #inventory['local'] = [ '127.0.0.1' ]

        query="SELECT Hostname,Role from inventory ORDER BY 1, 2;"
        data=execute_sql(query,raw=True)[0]

        for row in data:
                group = row[1]
                if group is None:
                        group = 'ungrouped'

                # Add group with empty host list to inventory{} if necessary
                if not group in inventory:
                        inventory[group] = {
                                'hosts' : []
                                }
                        inventory[group]['hosts'].append(row[0])
        print (json.dumps(inventory, indent=4))
        sys.exit(0)
# +----------------------------------------------------------------------+
def hostinfo(name):

    vars = {}

    query="""SELECT COUNT(*) FROM inventory WHERE Hostname='%s'""" %(name)
    data=execute_sql(query,raw=True)[0]

    #row = cur.fetchone()
    if data[0] == 0:
        print (json.dumps({}))
        sys.exit(0)

    # Inject some variables for all hosts
    vars = {
        'admin'         : 'Juned Memon',
        'datacenter'    : 'colo'
    }

    # Assuming you *know* that certain hosts need special vars
    # and you can't or don't want to use host_vars/ group_vars,
    # you could specify them here. For example, I *know* that
    # hosts with the word 'ldap' in them need a base DN

    if 'ldap' in name.lower():
        vars['baseDN'] = 'dc=mens,dc=de'


    print (json.dumps(vars, indent=4))

# +----------------------------------------------------------------------+
def show (args) :
        machine=args.machine
        role=args.role
        product=args.product
        owner=args.owner

        #query='SELECT * FROM inventory'
        query='SELECT i.Hostname,i.DC,i.Crid,i.Asset_ID,i.Price,i.Role,i.Product,i.Owner,f.Last_Update,f.Arch,f.Distribution,f.Version,f.System,f.Eth0_ip FROM inventory AS i LEFT JOIN facts AS f ON i.Hostname = f.Hostname'

        if machine:
                #query1 = query + (" WHERE  Hostname=%s" %machine)
                query1 = query + " where i.Hostname='" + machine + "'"

        elif role:
                query1 = query + " where i.Role like '%" + role + "%'"

        elif product:
                query1 = query + " where i.Product like '%" + product + "%'"

        elif owner:
                query1 = query + " where i.Owner like '%" + owner + "%'"

        else :
                query1 = query
        data=execute_sql(query1)[0]
        print (data)
        return 0
# +----------------------------------------------------------------------+
def reap (args) :
        machine=args.machine
        query='DELETE FROM inventory'
        query1 = query + " where Hostname='" + machine + "'"
        data=execute_sql(query1)[1]
        if (data==1):
                print ("Successfully Removed %s from Inventory" %(machine))
        return 0
# +----------------------------------------------------------------------+
def assign(args):
	#Before anything starts we need sojourner to create the roles/cookbook directory in the sojorner home
	init ()	
        machine=args.machine
        product=args.product
        role=args.role
	print (role)
        debug=args.debug
        if C.SOJOURNER_PROVISIONER == 'chef':
                path=C.SOJOURNER_CHEF_COOKBOOKS
        if C.SOJOURNER_PROVISIONER == 'ansible':
                path=C.SOJOURNER_ANSIBLE_ROLES
        if not os.path.exists(path+"/"+role):
                print ("Role path %s does not exist " %(path+"/"+role))
                exit(1)
	
	#Now we have confirmed that the role/cookbook path exists, lets set the environment
	os.environ['ANSIBLE_ROLES_PATH'] = str(C.SOJOURNER_ANSIBLE_ROLES)
	
        # Creat a Temp inventory file for this server
        content="[all]\n"
        tab="\t"
        content=content+machine+ "\tProduct=" + product + "\tRole=" + role + "\n"
        hostfile="/tmp/"+machine+".yml"
        fo = open(hostfile, "wb")
        fo.write(content);
        fo.close()

        playbook="/tmp/playbook/"
        if not os.path.exists(playbook):
                os.makedirs(playbook)
        playbook=playbook+role+".yml"

        content="""---
- name: Deploy %s
  hosts: all
  user: root

"""%(role)
        if C.SOJOURNER_PROVISIONER == 'chef':
                content=content+"""
  roles:
    -  { role: chef_zero,cookbook: %s }
    -  sojourner
""" %(role)
        elif C.SOJOURNER_PROVISIONER == 'ansible':
                content=content+"""
  roles:
    -  %s
    -  sojourner
""" %(role)



        fo = open(playbook, "wb")
        fo.write(content);
        fo.close()

        cmd="ansible-playbook -i "+ hostfile + " " + playbook
        if debug:
                OUT=None
        else:
                OUT=PIPE
        #status,output = commands.getstatusoutput(cmd)
        #status=subprocess.call(cmd,,stdout=OUT,stderr=OUT,shell=True)
        p=Popen(cmd.split(),stdout=OUT,stderr=OUT)
        output=p.communicate()
        status=p.returncode
        if status == 0:
                #Cool playbook run successfull"
                print ("Successfully Deployed  %s/%s on %s " %(product,role,machine))
        else:
                print ("Error:")
                print (output)


        #os.remove(hostfile)
        #os.remove(playbook)
        return 0
# +----------------------------------------------------------------------+
def listroles(args):
	init()
	print ("Provisioner is %s" %(C.SOJOURNER_PROVISIONER))
	if C.SOJOURNER_PROVISIONER == 'ansible':
        	OUT=None
        	cmd="ansible-galaxy list -p " + C.SOJOURNER_ANSIBLE_ROLES
        	p=Popen(cmd.split(),stdout=OUT,stderr=OUT)
        	output=p.communicate()
        	status=p.returncode
        	exit(status)
	if C.SOJOURNER_PROVISIONER == 'chef':
		OUT=None
		cmd="knife cookbook list --config " + C.DEFAULT_SOJOURNER_HOME + "knife.rb"
	        p=Popen(cmd.split(),stdout=OUT,stderr=OUT)
                output=p.communicate()
                status=p.returncode
                exit(status)
# +----------------------------------------------------------------------+
def init ():
	# Create the sojourner_home if not exist
	sojourner_home = C.DEFAULT_SOJOURNER_HOME
	ansible_roles  = C.SOJOURNER_ANSIBLE_ROLES
	chef_cookbooks = C.SOJOURNER_CHEF_COOKBOOKS
	for dir in C.DEFAULT_SOJOURNER_HOME,C.SOJOURNER_ANSIBLE_ROLES,C.SOJOURNER_CHEF_COOKBOOKS : 
		if os.path.isdir(dir):
			pass
		else :
			os.mkdir(dir)
	knife_file = C.DEFAULT_SOJOURNER_HOME + 'knife.rb'
	if os.path.isfile(knife_file):
		pass
	else:
	#Now copy the knife.rb file from /etc/sojourner to SOJOURNER_HOME
		content = '''log_level                :error
log_location             STDOUT
local_mode   true
cookbook_path ['%s' ]
''' %(C.SOJOURNER_CHEF_COOKBOOKS)

		fo = open(knife_file, "wb")
        	fo.write(content);
        	fo.close()
# +----------------------------------------------------------------------+
