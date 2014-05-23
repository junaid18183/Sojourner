#!/usr/bin/env python

import sqlite3
import sys
try:
    import json
except ImportError:
    import simplejson as json

dbname = '/home/junedm/ansible_home/inventory.db'

def grouplist(conn):

    inventory ={}

    # Add group for [local] (e.g. local_action). If needed,
    # set ansible_python_interpreter in host_vars/127.0.0.1
    #inventory['local'] = [ '127.0.0.1' ]

    cur = conn.cursor()
    cur.execute("SELECT Hostname,Role FROM inventory ORDER BY 1, 2")

    for row in cur.fetchall():
        group = row['Role']
        if group is None:
            group = 'ungrouped'
        
        # Add group with empty host list to inventory{} if necessary
        if not group in inventory:
            inventory[group] = {
                'hosts' : []
            }
        inventory[group]['hosts'].append(row['Hostname'])

    cur.close()
    print json.dumps(inventory, indent=4)

def hostinfo(conn, name):

    vars = {}

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM hosts WHERE name=?", (name, ))

    row = cur.fetchone()
    if row[0] == 0:
        print json.dumps({})
        sys.exit(0)

    # Inject some variables for all hosts
    vars = {
        'admin'         : 'Jane Jolie',
        'datacenter'    : 1
    }

    # Assuming you *know* that certain hosts need special vars
    # and you can't or don't want to use host_vars/ group_vars,
    # you could specify them here. For example, I *know* that
    # hosts with the word 'ldap' in them need a base DN

    if 'ldap' in name.lower():
        vars['baseDN'] = 'dc=mens,dc=de'


    print json.dumps(vars, indent=4)


if __name__ == '__main__':
    con = sqlite3.connect(dbname)
    con.row_factory=sqlite3.Row

    if len(sys.argv) == 2 and (sys.argv[1] == '--list'):
        grouplist(con)
    elif len(sys.argv) == 3 and (sys.argv[1] == '--host'):
        hostinfo(con, sys.argv[2])
    else:
        print "Usage: %s --list or --host <hostname>" % sys.argv[0]
        sys.exit(1)

    con.close()
