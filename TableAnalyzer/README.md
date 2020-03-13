
# cassandra.toolkit/TableAnalyzer 
A Cassandra (CFStats/TableStats) output analyzer that visualizes variance in metrics between nodes. This is the first of many tools I've been working on that help understand what's going on in a Cassandra cluster. It's not supposed to replace OpsCenter, Prometheus+Grafana, or other tools out there. The goal is to eventually build intelligence in here to help people build better tables through analysis of the keys, etc. 

This tool was created because we had a hard time explaining to non-believers that data-model issues were the reason their "amazing app" crashed all the time, and that it wasn't Cassandra's fault. 

The first tool in the Cassandra Vision toolset is Table Analyzer which can collect the cfstats/tablestates by
1. The extracted contents of a diagnostics tarball from DSE OpsCenter
2. Via `nodetool cfstats` or `nodetool tablestats` from a local DSE / Cassandra / Elassandra / Scylla instance (Only tested with DSE/Cassandra)
3. Via `nodetool` (Above) through SSH 

Once it has the stats, it parses and transforms into a CSV file format, which then is transformed again into conditionally formatted Excel file (xlsx). 
It also creates the data set as JSON which can be then sent to ElasticSearch, New Relic, etc. for further visualization. 

The very original original original code came from "https://github.com/thejaspm/cfstatsParseVisualize" which has been worked over several times. In the spirit of open source, credit goes to https://github.com/thejaspm for starting it off.  



## Backlog

1. Fix Dockerized test bed and put into /TableAnalyzer/docker w/ Compose file 
2. Test Cassandra Vision React GridView SPA App + API pulling data from Cassandra 
3. Create Dockerized service w/ options to use internal Cassandra or external + Gridview
4. Add ability to add Environments/Clusters in web interface 


## Credits

1. Rahul Singh - Concept, Initial Version
2. Tom Hada - Refactoring, Code Cleanup
3. Rohan Bane - Refactoring, Dockerization, Gridview Start
4. Jagannath Bilgi - Refactoring, Testing
5. Shridhar Nandeshwar - Testing, User Feedback
6. Senthilvel Palaniappan - Testing, User Feedback
7. Ameer Ajmal Baig - Testing, User Feedback
8. Pramod Pottimuthu - Testing, User Feedback
9. Clyde Clark - Testing, Documentation, User Feedback

# Installation 

Make sure to use pip3 / python3. Needs pandas, statistics for analysis tool 

## prerequisities
- pandas
- statistics
- xlsxwriter 
- openpyxl
- pyyaml

Install using `pip3 install -r requirements.txt` `pip install -r requirements.txt`

## How to use

1. In the home directory, in a folder `config`, create the file `environments.yaml` if it does not yet exist using a copy of `environments-sample.yaml`
2. In the home directory, in a folder `keys`, add pem files needed to ssh into each node to be analyzed - reference these in your `environments.yaml`
3. Run `cfstats.receive.py region cluster datacenter` to get table data from a specific datacenter (see `environments.yaml`)
4. Run `cfstats.transform.py region cluster datacenter` to transform the retrieved data into json, csv, and xlsx files
5. Run `csv2formattedxls.py data/region/cluster/region.cluster.cfstats.pivot.csv data/region/cluster/region.prod.cfstats.xlsx` to pivot the data into a formatted excel file 


## environments.yaml

```
us:
  prod:
    cassandra:
      - 192.168.0.1
      - 192.168.0.2
      - 192.168.0.3
    spark:
      - 192.168.0.4
    key: keyfile.pem
  prod2:
    cassandra:
      - 192.168.0.11
      - 192.168.0.12
      - 192.168.0.13
    spark:
      - 192.168.0.14
    key: keyfile.pem 
  stage:
    cassandra:
      - 192.168.1.1
      - 192.168.1.2
      - 192.168.1.3
    spark:
      - 192.168.1.4
    key: keyfile.pem 
region:
  cluster:
    datacenter:
```


