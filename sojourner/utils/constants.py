
# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import pwd
import sys

from string import ascii_letters, digits
from ConfigParser import SafeConfigParser

# copied from utils, avoid circular reference fun :)
def mk_boolean(value):
    if value is None:
        return False
    val = str(value)
    if val.lower() in [ "true", "t", "y", "1", "yes" ]:
        return True
    else:
        return False

def get_config(p, section, key, env_var, default, boolean=False, integer=False, floating=False, islist=False):
    ''' return a configuration variable with casting '''
    value = _get_config(p, section, key, env_var, default)
    if boolean:
        return mk_boolean(value)
    if value and integer:
        return int(value)
    if value and floating:
        return float(value)
    if value and islist:
        return [x.strip() for x in value.split(',')]
    return value

def _get_config(p, section, key, env_var, default):
    ''' helper function for get_config '''
    if env_var is not None:
        value = os.environ.get(env_var, None)
        if value is not None:
            return value
    if p is not None:
        try:
            return p.get(section, key, raw=True)
        except:
            return default
    return default

def load_config_file():
    ''' Load Config File order(first found is used): ENV, CWD, HOME, /etc/sojourner '''

    p = SafeConfigParser()

    path0 = os.getenv("SOJOURNER_CONFIG", None)
    if path0 is not None:
        path0 = os.path.expanduser(path0)
    path1 = os.getcwd() + "/sojourner.cfg"
    path2 = os.path.expanduser("~/.sojourner.cfg")
    path3 = "/etc/sojourner/sojourner.cfg"

    for path in [path0, path1, path2, path3]:
        if path is not None and os.path.exists(path):
            try:
                p.read(path)
            except configparser.Error as e:
                print("Error reading config file: \n{0}".format(e))
                sys.exit(1)
            return p
    return None

def shell_expand_path(path):
    ''' shell_expand_path is needed as os.path.expanduser does not work
        when path is None, which is the default for SOJOURNER_PRIVATE_KEY_FILE '''
    if path:
        path = os.path.expanduser(os.path.expandvars(path))
    return path

p = load_config_file()

active_user   = pwd.getpwuid(os.geteuid())[0]

# sections in config file
DEFAULTS='defaults'

# configurable things
# 			def get_config(p, section, key, env_var, default, boolean=False, integer=False, floating=False, islist=False):
DEFAULT_SOJOURNER_HOME    = shell_expand_path(get_config(p, DEFAULTS, 'sojourner_home','DEFAULT_SOJOURNER_HOME',False))
DEFAULT_DB_ENGINE         = get_config(p, DEFAULTS, 'db_engine', 'SOJOURNER_DB_ENGINE', 'sqlite')
DEFAULT_DB_HOST         = get_config(p, DEFAULTS, 'db_host', 'SOJOURNER_DB_HOST', 'localhost')
DEFAULT_DB_PORT         = get_config(p, DEFAULTS, 'db_port', 'SOJOURNER_DB_PORT', '3306')
DEFAULT_DB_USER         = get_config(p, DEFAULTS, 'db_user', 'SOJOURNER_DB_USER', 'sojourner')
DEFAULT_DB_PASSWD         = get_config(p, DEFAULTS, 'db_passwd', 'SOJOURNER_DB_PASSWD', 'sojourner')
DEFAULT_DB_DBNAME         = get_config(p, DEFAULTS, 'db_dbname', 'SOJOURNER_DB_DBNAME', 'sojourner')


SOJOURNER_PROVISIONER            = get_config(p, 'sojourner', 'provisioner', 'SOJOURNER_PROVISIONER', 'ansible')

# ANSIBLE RELATED
SOJOURNER_ANSIBLE_ROLES               = get_config(p, 'ansible', 'ansible_roles', 'SOJOURNER_ANSIBLE_ROLES','/root/Sojourner/ansible_roles')

# CHEF RELATED
SOJOURNER_CHEF_COOKBOOKS = get_config(p, 'chef', 'chef_cookbooks', 'SOJOURNER_CHEF_COOKBOOKS','/root/Sojourner/chef_cookbooks')
