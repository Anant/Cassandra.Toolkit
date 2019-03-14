import sys
from cassandra.cluster import Cluster
import pandas as pd
import datetime
import argparse

parser = argparse.ArgumentParser(
    description='Collecting config varibales from environments.yaml and Start receiving stats',
    usage='{region} {environment} [host] [keyspace] [table] ')
parser.add_argument('region', type=str, help='Region {us-east-1|usw|us|aws}')
parser.add_argument('environ', type=str, help='Environment {dev|stage|prod}')
parser.add_argument('host', type=str, help='Host name')
parser.add_argument('keyspace', type=str, help='Keyspace name')
parser.add_argument('table', type=str, help='Table name')

args = parser.parse_args()


def main():
    cluster = Cluster()
    session = cluster.connect()
    gotSesssion = False
    metaData = cluster.metadata
    keySpaceList = []
    tableList = []


    for keyspaces in metaData.keyspaces:
        keySpaceList.append(keyspaces)
    if 'tableanalyzer' not in keySpaceList:
        print ("Keyspace Not Present Creating The Keyspace 'tableanalyzer'")
        result = session.execute("CREATE KEYSPACE tableanalyzer WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy','datacenter1' : 3 }")
        print(result)
        metaData = cluster.metadata
        keySpaceList = []
        for keyspaces in metaData.keyspaces:
            keySpaceList.append(keyspaces)
        if 'tableanalyzer' in keySpaceList:
            ("Succesfully Created The Keyspace 'tableanalyzer'")
        else:
            print ("Unable To Create Keyspace 'tableanalyzer', Terminating The Code")
            sys.exit()


    session = cluster.connect('tableanalyzer')
    metaData = cluster.metadata
    keyspace = metaData.keyspaces['tableanalyzer']


    for table in keyspace.tables:
        tableList.append(table)
    if 'stats_by_date' not in tableList:
        print("Table 'stats_by_date' Not Present, Creating New Table")
        result = session.execute("CREATE TABLE stats_by_date ("+
                                 "stat_date date,"+
                                 "host text,"+
                                 "keyspace_name text,"+
                                 "tablename text,"+
                                 "stats text,"+
                                 "PRIMARY KEY (stat_date, host, keyspace_name, tablename)"+
                                 ");")
        metaData = cluster.metadata
        tableList = []
        keyspace = metaData.keyspaces['tableanalyzer']
        for table in keyspace.tables:
            tableList.append(table)
        if 'stats_by_date' in tableList:
            ("Succesfully Created The Table 'stats_by_date'")
        else:
            print ("Unable To Create Table 'stats_by_date', Terminating The Code")
            sys.exit()

    path = str("data/"+args.region+"/"+args.environ+"/"+args.region+"."+args.environ+".cfstats.csv")
    data = pd.read_csv(path)
    dataArray = []

    date = datetime.date.today()
    dataToSend = str(data)

    query = "INSERT INTO tableanalyzer.stats_by_date (stat_date, host, keyspace_name, tablename,stats) VALUES ('"+str(date)+"','"+args.host+"','"+args.keyspace+"','"+args.table+"','"+dataToSend+"');"

    result = session.execute(query)

if __name__ == '__main__':
    main()
