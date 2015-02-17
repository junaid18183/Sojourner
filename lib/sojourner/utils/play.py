# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

#In Python 3, the keyword print has been changed from calling a statement to calling a function.
#So instead of saying print value you now need to say print(value), or you'll get a SyntaxError.

__metaclass__ = type
# +----------------------------------------------------------------------+
from sojourner.utils.dbcon import *

# +----------------------------------------------------------------------+
def deploy_local_fact(product,role,fact_dest):
	playbook="/tmp/playbook/"
        if not os.path.exists(playbook):
                os.makedirs(playbook)
        playbook=playbook+role+".yml"

        content="""---
- name: Deploy %s
  hosts: all
  user: root

  vars :
   - Dest : %s
"""%(role,fact_dest)

        if C.SOJOURNER_PROVISIONER == 'chef':
                content=content+"""
  roles:
    -  { role: chef_zero,cookbook: %s }
""" %(role)
        elif C.SOJOURNER_PROVISIONER == 'ansible':
                content=content+"""
  roles:
    -  %s
""" %(role)

#Now the role section is added, lets add post_task

        product_regex=r"'Product=((?!{{Product}})[\w\s]+)\n'"
        product_replace=r"'Product={{Product}} \1\n'" ## I have added r infront of string to make it raw, otherwise \1 was getting converted to hex
        role_regex=r"'Role=((?!{{Role}})[\w\s]+)\n'"
        role_replace=r"'Role={{Role}} \1\n'"
        line_regex=r"'\[setup\][\n]Product=[\w\s]*[\n]Role=[\w\s]+'"
        line_line=r"'[setup]\nProduct={{Product}}\nRole={{Role}}'"

        content=content+"""
  post_tasks:

  - name : Check if {{Dest}} exist's
    stat: path={{ Dest }}
    register: st

  - replace : dest={{ Dest }}  regexp=%s  replace=%s
    when:  st.stat.exists is defined and st.stat.exists==True
  - replace : dest={{ Dest }}  regexp=%s  replace=%s
    when:  st.stat.exists is defined and st.stat.exists==True

  - lineinfile : dest={{ Dest }}  regexp=%s  line=%s create=yes mode=644
    when:  st.stat.exists is defined and st.stat.exists==False

  - setup:

""" %( product_regex,product_replace,role_regex,role_replace,line_regex,line_line)

# repr is used to escape the \n, otherwise it will literally add the newline
# Complete playbook is written

	fo = open(playbook, "wb")
        fo.write(content);
        fo.close()
	return playbook
# +----------------------------------------------------------------------+
def reap_local_fact(fact_dest):
	playbook="/tmp/playbook/"
        if not os.path.exists(playbook):
                os.makedirs(playbook)
        playbook=playbook+"reap.yml"
        dest = "/etc/ansible/facts.d/sojourner.fact"
        content="""---
- name: Reap LocalFacts for reaping
  hosts: all
  user: root

  vars :
   - Dest : %s

  tasks:
  - name : Check if {{Dest}} exist's
    stat: path={{ Dest }}
    register: st

  - file: path={{ Dest }}  state=absent
    when:  st.stat.exists is defined and st.stat.exists==True

  - setup:

"""%(fact_dest)
	fo = open(playbook, "wb")
        fo.write(content);
        fo.close()
        return playbook
# +----------------------------------------------------------------------+
def create_temp_inventory_file (machine,product="",role=""):
 # Creat a Temp inventory file for this server
        content="[all]\n"
        tab="\t"
        content=content+machine+ "\tProduct=" + product + "\tRole=" + role + "\n"
        hostfile="/tmp/"+machine+".yml"
        fo = open(hostfile, "wb")
        fo.write(content);
        fo.close()
	return hostfile
# +----------------------------------------------------------------------+
def run_playbook (hostfile,playbook,debug):
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
	
        #os.remove(hostfile)
        #os.remove(playbook)
	
	return status

# +----------------------------------------------------------------------+
