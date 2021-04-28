# Debugging
Some errors you might run into and possible solutions

## ERROR: chown failed: failed to look up user
E.g., 

```
TASK [cassandra-exporter-install : create cassandra_exporter folder] ***************************************************************************fatal: [139.59.255.44]: FAILED! => {"changed": false, "gid": 0, "group": "root", "mode": "0755", "msg": "chown failed: failed to look up user cassandra", "owner": "root", "path": "/usr/share/dse/cassandra_exporter", "size": 4096, "state": "directory", "uid": 0}
```

In your `group_vars/all.yml` file the `cassandra_ops_os_user` var is set to `cassandra`. Make sure this value corresponds to the linux username for the node.

## ERROR: value of state must be one of: absent, build-dep, fixed, latest, present, got: installed
E.g., 
```
TASK [tablesnap-install : install python2-pip] *************************************************************************************************[DEPRECATION WARNING]: Invoking "yum" only once while using a loop via squash_actions is deprecated. Instead of using a loop to supply multiple
 items and specifying `name: "{{ item }}"`, please use `name: ['python2-pip']` and remove the loop. This feature will be removed in version
2.11. Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
failed: [139.59.255.44] (item=[u'python2-pip']) => {"ansible_facts": {"pkg_mgr": "apt"}, "ansible_loop_var": "item", "changed": false, "item": ["python2-pip"], "msg": "value of state must be one of: absent, build-dep, fixed, latest, present, got: installed"}
```

### Solution: 

Make sure your host has python2 and pip2 installed by the linux package manager. 

See here for ansible docs related to this issue (these docs specifically for using a node that uses `apt`):
https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html#apt-manages-apt-packages

For this error in particular, using `apt` package manager on the target host:

```
apt install python
apt install python-pip
```