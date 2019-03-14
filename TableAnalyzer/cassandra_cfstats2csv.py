import sys
import csv
import time
import os
import re
import platform
import argparse
import json

"""
This script parses through `nodetool -h localhost cfstats` output, and creates CSV files. 
"""


def cfstats(path):
    return open(path).read().split("\n")

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
    cf = ''
    exclude_ks = ["system", "cfs", "cfs_archive", "HiveMetaStore", "OpsCenter", "dse_perf", "dse_security",
                  "dse_system", "system_traces", "dsefs", "dse_leases", "dse_analytics"]

    try:
        with open('config/parsingMap.json', 'r') as f:
            map = json.load(f)
            if version == 2:
                mapper = map['cfstats']
            elif version == 3:
                mapper = map['tablestats']
    except FileNotFoundError:
        print("parsingMap.json File Not Found OR Error While Getting Setting Parameters, Terminating The Code")
        sys.exit()

    for line in cfstats(path):
        # here we go
        if "Keyspace :" in line:
            # if it's a new keyspace, reset cf name
            ks = (line.split(":")[1]).strip()
            cf = "keyspace"

        # we are only interested in non-internal keyspaces
        if (ks not in exclude_ks):
            if "Table:" in line:
                cf = (line.split(":")[1]).strip()

        for key, val in mapper.items():
            if (str(line) != "") & (str(line).find(":") != -1):
                line_key, line_val = line.split(":")
                if key.lower() in line_key.lower():
                    if "NaN" in line_val:
                        line_val = 0
                    else:
                        line_val = find_numbers(line_val)[0]
                    data.append([hostname, ks, cf, val, line_val, timestamp])

    # send gathered data to carbon server
    # message = '\n'.join(data) + '\n'
    with open(save, "w", newline="") as f:
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
