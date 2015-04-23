# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

#In Python 3, the keyword print has been changed from calling a statement to calling a function.
#So instead of saying print value you now need to say print(value), or you'll get a SyntaxError.

__metaclass__ = type
# +----------------------------------------------------------------------+
from sojourner.utils.dbcon import *
import os
from jinja2 import Environment, FileSystemLoader

#------------------------------------------------------------------------------------------------
 
PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)

OUTPUT_FILE="output.yml" 

role = 'mysql'
puppet_home = '/var/tmp/sojourner/puppet'
Sojourner_Puppet_Home = '/root/Sojourner/Puppet_Manifests'

context = {
        'role': role ,
        'puppet_home' : puppet_home ,
        'Sojourner_Puppet_Home' : Sojourner_Puppet_Home
    }   
#------------------------------------------------------------------------------------------------
def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
 
#------------------------------------------------------------------------------------------------
def create_playbook ():
    fname = OUTPUT_FILE

    with open(fname, 'w') as f:
        output = render_template('base.yml', context)
        f.write(output)

    with open(fname, 'a') as f:
        output = render_template('puppet.yml', context)
        f.write(output)

#------------------------------------------------------------------------------------------------
 
def main():
	create_playbook () 
#------------------------------------------------------------------------------------------------
 
if __name__ == "__main__":
    main()
