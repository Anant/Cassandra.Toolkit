# Log analysis with filebeat, elasticsearch & kibana

### Install all
Say hello to server to make sure ssh works. If you are running on localhost make an entry like this in your hosts.ini so you can bypass SSH.

```
localhost ansible_connection=local
```

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
- playbook for redhat 
- Redhat on ansible 
```
https://www.elastic.co/guide/en/elasticsearch/reference/current/rpm.html
https://www.elastic.co/guide/en/kibana/current/rpm.html
https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-installation.html
```
