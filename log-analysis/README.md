# Log analysis with filebeat, elasticsearch & kibana

### Install all
Say hello to server to make sure ssh works
```
ansible-playbook -i ./envs/elk/hosts.ini ./playbooks/hello.yml
```
The next command installs:
- install elasticsearch
- install kibana
- install logstash
- install filebeats

```
ansible-playbook -i ./envs/elk/hosts.ini ./playbooks/elk-install.yml
```

ToDo:
- run elasticsearch with docker
