# Debugging
Some errors you might run into and possible solutions

## ERROR: chown failed: failed to look up user
E.g., 

```
TASK [cassandra-exporter-install : create cassandra_exporter folder] ***************************************************************************fatal: [139.59.255.44]: FAILED! => {"changed": false, "gid": 0, "group": "root", "mode": "0755", "msg": "chown failed: failed to look up user cassandra", "owner": "root", "path": "/usr/share/dse/cassandra_exporter", "size": 4096, "state": "directory", "uid": 0}
```

In your `group_vars/all.yml` file the `cassandra_ops_os_user` var is set to `cassandra`. Make sure this value corresponds to the linux username for the node.

# AnsibleUndefinedVariable: 'aws_access_key_id' is undefined
E.g., 

```
TASK [tablesnap-install : install systemd tablesnap.service unit] ******************************************************************************failed: [139.59.255.44] (item=tablesnap.service) => {"ansible_loop_var": "item", "changed": false, "item": "tablesnap.service", "msg": "AnsibleUndefinedVariable: 'aws_access_key_id' is undefined"}
```

Make sure to send in `aws_access_key_id` using the `-e` flag when calling `ansible-playbook`, or specifying in the `group_vars/all.yml` file for your ansible env.

## ERROR The next_nth_usable filter requires python's netaddr be installed on the ansible controller

E.g., 
```
fatal: [localhost]: FAILED! => {"msg": "The next_nth_usable filter requires python's netaddr be installed on the ansible controller"}
```

This is from the `localhost` commands from `src/ansible/playbooks/cassandra-tools-install.yml`

### Solution

You need to install a python lib on your ansible controller, as mentioned [in this issue](https://github.com/ansible/workshops/issues/115#issuecomment-635844085). 
```
apt install --no-install-recommends python-netaddr
```