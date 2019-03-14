# cassandra-vision
A Cassandra (CFStats/TableStats) output analyzer that visualizes variance in metrics between nodes. 

## TableAnalyzer 

The first tool in the Cassandra Vision toolset is Table Analyzer which can collect the cfstats/tablestates by
1. The extracted contents of a diagnostics tarball from DSE OpsCenter
2. Via `nodetool cfstats` or `nodetool tablestats` from a local DSE / Cassandra / Elassandra / Scylla instance (Only tested with DSE/Cassandra)
3. Via `nodetool` (Above) through SSH 

Once it has the stats, it parses and transforms into a CSV file format, which then is transformed again into conditionally formatted Excel file (xlsx). 
It also creates the data set as JSON which can be then sent to ElasticSearch, New Relic, etc. for further visualization. 

The very original original original code came from "https://github.com/thejaspm/cfstatsParseVisualize" which has been worked over several times. In the spirit of open source, credit goes to https://github.com/thejaspm for starting it off.  