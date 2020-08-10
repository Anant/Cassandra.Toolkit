import sys
import csv
import time
import os
import re
import platform
import argparse
import json
import numpy as np

"""
This script parses through `nodetool -h localhost cfstats` output, and creates CSV files. 
"""


def cfstats(path):
    return open(path).read().split("----------------")   #split by keyspaces

def find_numbers(string, ints=True):
    numexp = re.compile(r'[-]?\d[\d,]*[\.]?[\d{2}]*') #optional - in front
    numbers = numexp.findall(string)
    numbers = [x.replace(',','') for x in numbers]
    if ints is True:
        return [int(x.replace(',','').split('.')[0]) for x in numbers]
    else:
        return numbers

def generate(path, save, version):
    hostname = path.replace("tables/", " ")
    timestamp = int(time.time())
    data = []
    ks = ''
    #cf = ''
    exclude_ks = ["system", "cfs", "cfs_archive", "HiveMetaStore", "OpsCenter", "dse_perf", "dse_security","solr_admin","dse_insights_local","dse_system", "system_traces", "dsefs", "dse_leases", "dse_analytics","system_schema","dse_insights","system_distributed","dse_system_local","system_auth"]
    mapper={} 
    try:
         
        with open('config/parsingMap.json', 'r') as f:
            map = json.load(f)
        
            if  int(sys.argv[4]) == 2:
                for i,v in map['cfstats'].items():
                    mapper[i] = v
            elif int(sys.argv[4]) == 3:
                for i,v in map['tablestats'].items():
                    mapper[i] = v
            #print(mapper)
        
         
    except FileNotFoundError:
        print("parsingMap.json File Not Found OR Error While Getting Setting Parameters, Terminating The Code")
        sys.exit()

    #print(cfstats(path))
    for line in cfstats(path): # iterating each keyspace
        # here we go
       cf=[]
       
       if "Keyspace :" in line or "Keyspace:" in line:
            #print("keyspace found")
            # if it's a new keyspace, reset cf name
            ks1 = (line.split(":")[1]).split("\n")[0].strip()
    
            if ks1 not in exclude_ks:   #condition to check if the keyspace is not in exclude_ks list
                print("keyspace not in exclude list")
                if "Table:" in line or "Table (index)" in line:    #get the table name from each keyspace
                    for i in (line.split("\n\t\t")):
                        if ('Table'  == (i.split(":")[0]) or 'Table (index)'  == (i.split(":")[0])):
                            cf.append (i.split(":")[1].strip()) # list of tables in each keyspace
                            cf1=i.split(":")[1].strip() # for current table in progress in each keyspace
            
                        for key, val in mapper.items():
                        
                            line_key = (i.split(":")[0].strip())  #key 
                            line_val = (i.split(":")[1].strip())  #value
                        
                            if key.lower() in line_key.lower():
                               if "NaN" in line_val:
                                   line_val = 0
                               else:
                                   line_val = find_numbers(line_val)[0]
                               data.append([hostname, ks1, cf1, val, line_val, timestamp])
                                 

                                         

    
    with open(save, "w") as f:
        writer = csv.writer(f)
        for line in data:
            writer.writerow(line)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converting Stats Form TXT TO CSV Format',
        usage='{path} {save} {2|3}')
    parser.add_argument('path', type=str, help='Path of txt file of Stats')
    parser.add_argument('save', type=str, help='Path of file to save CSV File')
    parser.add_argument('version', type=str, help='Cassandra Version')
    args = parser.parse_args()
    if generate(args.path, args.save, args.version):
        print("Success.")
