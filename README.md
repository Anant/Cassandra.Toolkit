# cassandra-vision
A curated + created set of useful Cassandra / Cassandra compatible tools specifically for Visualizing Cassandra cluster related things. Maintained by Rahul Singh of [Anant](http://anant.us). Feel free contact me if you'd like to collaborate on this and other tools. I also work on [Cassandra.Link](http://cassandra.link), a curated set of knowledge on all things related to Cassandra. Please take a look!


## TableAnalyzer 
A Cassandra (CFStats/TableStats) output analyzer that visualizes variance in metrics between nodes. This is the first of many tools I've been working on that help understand what's going on in a Cassandra cluster. It's not supposed to replace OpsCenter, Prometheus+Grafana, or other tools out there. The goal is to eventually build intelligence in here to help people build better tables through analysis of the keys, etc. 

This tool was created because we had a hard time explaining to non-believers that data-model issues were the reason their "amazing app" crashed all the time, and that it wasn't Cassandra's fault. 

The first tool in the Cassandra Vision toolset is Table Analyzer which can collect the cfstats/tablestates by
1. The extracted contents of a diagnostics tarball from DSE OpsCenter
2. Via `nodetool cfstats` or `nodetool tablestats` from a local DSE / Cassandra / Elassandra / Scylla instance (Only tested with DSE/Cassandra)
3. Via `nodetool` (Above) through SSH 

Once it has the stats, it parses and transforms into a CSV file format, which then is transformed again into conditionally formatted Excel file (xlsx). 
It also creates the data set as JSON which can be then sent to ElasticSearch, New Relic, etc. for further visualization. 

The very original original original code came from "https://github.com/thejaspm/cfstatsParseVisualize" which has been worked over several times. In the spirit of open source, credit goes to https://github.com/thejaspm for starting it off.  

Eventually we want compatability for the following items. 


||Platform||Receive||Transform||
|DSE 4.8.x|Diagnostic Tarball|Y|
|DSE 4.8.x/C* 2.1.x|Nodetool|Y|
|DSE 4.8.x/C* 2.1.x|SSH|Y|
|DSE 5.1.x|Diagnostic Tarball|Y|
|DSE 5.1.x/C* 3.1.x|Nodetool|Y|
|DSE 5.1.x/C* 3.1.x|SSH|Y|
|DSE 6.7.x|Diagnostic Tarball|Y|
|DSE 6.7.x/C* 4.0.x|Nodetool|Y|
|DSE 6.7.x/C* 4.0.x|SSH|Y|
|Scylla?|Tarball|Y|
|Elassandra?|Tarball|Y|
|YugaByte?|Tarball|Y|
|CosmosDB?|Tarball|Y|
|AWS MCS?|Tarball|Y|


### Backlog

1. Fix Dockerized test bed and put into /TableAnalyzer/docker w/ Compose file 
2. Test Cassandra Vision React GridView SPA App + API pulling data from Cassandra 
3. Create Dockerized service w/ options to use internal Cassandra or external + Gridview
4. Add ability to add Environments/Clusters in web interface 
