#!/usr/bin/python

import pipes

DOCUMENTATION = '''
---
module: puppet
short_description: Runs puppet apply on remote host
description:
  - Runs I(puppet) apply  in a reliable manner
version_added: "3.7.4"
options:
  timeout:
    description:
      - How long to wait for I(puppet) to finish.
    required: false
    default: 30m
  manifest:
    description:
      - The absolute path of the manifest to apply
    required: true
  modulepath:
    description:
      - The aboslute path of the modulepath
    required: false
    default: system default (/etc/puppet/modules)
  hiera_config:
    description:
      - The aboslute path for hiera_config
    required: false
    default: system default (/etc/puppet/hiera)


  show_diff:
    description:
      - Should puppet return diffs of changes applied. Defaults to off to avoid leaking secret changes by default.
    required: false
    default: no
    choices: [ "yes", "no" ]
requirements: [ puppet ]
author: Juned Memon
'''

EXAMPLES = '''
# Run puppet apply and timeout in 5 minutes
- puppet: timeout=5m manifest=/tmp/site.pp

# Run puppet apply with custom module_path
-  puppet: manifest=/tmp/site.pp modulepath=/var/tmp/sojourner/puppet/modules 

# Run puppet apply with hiera config
-  puppet: manifest=/tmp/site.pp hiera_config=/var/tmp/sojourner/puppet/hieradata/hiera.yaml

'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            timeout=dict(default="30m"),
            manifest=dict(required=True),
            modulepath=dict(aliases=['module_path']),
            hiera_config=dict(aliases=['hiera-config']),
            show_diff=dict(
                default=False, aliases=['show-diff'], type='bool'),
        ),
    )
    p = module.params

    global PUPPET_CMD
    PUPPET_CMD = module.get_bin_path("puppet", False)

    if not PUPPET_CMD:
        module.fail_json(
            msg="Could not find puppet. Please ensure it is installed.")

    cmd = ("timeout -s 9 %(timeout)s %(puppet_cmd)s apply "
           " --detailed-exitcodes --verbose %(manifest)s") % dict(
               timeout=pipes.quote(p['timeout']), puppet_cmd=PUPPET_CMD,
               manifest=pipes.quote(p['manifest']))
    if p['show_diff']:
        cmd += " --show-diff"
  
    if p['modulepath']:
	cmd += " --modulepath=%s" %(p['modulepath'])  

    if p['hiera_config']:
        cmd += " --hiera_config==%s" %(p['hiera_config']) 

    rc, stdout, stderr = module.run_command(cmd)

    if rc == 0:
        # success
        module.exit_json(rc=rc, changed=False, stdout=stdout)
    elif rc == 1:
        # rc==1 could be because it's disabled
        # rc==1 could also mean there was a compilation failure
        disabled = "administratively disabled" in stdout
        if disabled:
            msg = "puppet is disabled"
        else:
            msg = "puppet did not run"
        module.exit_json(
            rc=rc, disabled=disabled, msg=msg,
            error=True, stdout=stdout, stderr=stderr)
    elif rc == 2:
        # success with changes
        module.exit_json(rc=0, changed=True)
    elif rc == 124:
        # timeout
        module.exit_json(
            rc=rc, msg="%s timed out" % cmd, stdout=stdout, stderr=stderr)
    else:
        # failure
        module.fail_json(
            rc=rc, msg="%s failed with return code: %d" % (cmd, rc),
            stdout=stdout, stderr=stderr)

# import module snippets
from ansible.module_utils.basic import *

main()
