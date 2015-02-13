# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

#In Python 3, the keyword print has been changed from calling a statement to calling a function.
#So instead of saying print value you now need to say print(value), or you'll get a SyntaxError.

__metaclass__ = type

# +----------------------------------------------------------------------+

from sojourner.utils.dbcon import *
from sojourner.utils.play import *

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
	debug=args.debug
	fact_dest = "/etc/ansible/facts.d/sojourner.fact"
	playbook=reap_local_fact(fact_dest)
	hostfile=create_temp_inventory_file(machine)
	status=run_playbook (hostfile,playbook,debug)
	if status == 0:
                #Cool playbook run successfull"
        	query='DELETE FROM inventory'
        	query1 = query + " where Hostname='" + machine + "'"
        	data=execute_sql(query1)[1]
        	if (data==1):
                	print ("Successfully Removed %s from Inventory" %(machine))
        else:
                print ("Error:")
                print (output)
        return 0
# +----------------------------------------------------------------------+
def assign(args):
	#Before anything starts we need sojourner to create the roles/cookbook directory in the sojorner home
	init ()	
        machine=args.machine
        product=args.product
        role=args.role
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
	hostfile=create_temp_inventory_file(machine,product,role)	

	fact_dest = "/etc/ansible/facts.d/sojourner.fact"
	playbook=deploy_local_fact (role,fact_dest)
	
	status=run_playbook (hostfile,playbook,debug)
	
        return status
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
