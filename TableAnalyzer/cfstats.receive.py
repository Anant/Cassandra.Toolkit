import argparse
import subprocess
import os
import sys
import config
import json
import pandas as pd
import re
import util

parser = argparse.ArgumentParser(
    description='Collecting config varibales from environments.yaml and Start receiving stats',
    usage=' {region} {environment} {datacenter} {0|1} [-k] [-t]')
parser.add_argument('region', type=str, help='Region {us-east-1|usw|us|aws}')
parser.add_argument('environ', type=str, help='Environment {dev|stage|prod}')
parser.add_argument('db', type=str, help='Database {cassandra|spark}')
parser.add_argument('debug', type=int, help='Debuger {0|1}')
parser.add_argument('-k', '--keySpace', default='', type=str, help='Name Of Keyspace')
parser.add_argument('-t', '--table', default='', type=str, help='Name Of Table')

args = parser.parse_args()


def main():
    useSSH = False
    detectTopology = True
    gotHeader = False
    nodeArray = []
    nodeTable = ''
    keys = []

    if args.debug: print("Checking " + args.db.title() + " Version")
    command = str("nodetool version")
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
    except subprocess.CalledProcessError as e:
        result = str(e.output)
        if result.find("Connection refused") >= 0:
            print("Cannot Connect To " + args.db.title() + ", Terminating code")
            sys.exit()
    if args.debug: print(args.db + " Version : " + output)

    if int((output.split(": ")[1])[0]) == 2:
        if args.debug: print("Cassandra Version v2 using nodetool cfstats")
        stats = str("cfstats")
    else:
        if args.debug: print("Cassandra Version v3 using nodetool tablestats")
        stats = str("tablestats")

    if (args.keySpace == "") & (args.table != ""):
        print("Please Provide the Key Space Before Table Using -k / --keySapace")
        sys.exit()

    print("Collecting config varibales from Config")

    try:
        with open('config/settings.json', 'r') as f:
            setting = json.load(f)
            useSSH = setting['connection']['useSSH']
            detectTopology = setting['connection']['detectTopology']
    except FileNotFoundError:
        print("settings.json File Not Found OR Error While Getting Setting Parameters, Applying Default Settings")

    if detectTopology:
        if args.debug: print("Detechting Nodes")
        command = str("nodetool status")
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
            dataArray = output.split("\n")
            for i in dataArray:
                if i != '':
                    if i.find("Note:") != -1:
                        continue
                    if i.find("--  Address") != -1:
                        header = re.sub(r'\s+',',',i).split(",")
                        header[5] = str(str(header[5])+str(header[6]))
                        del header[6]
                        gotHeader = True
                        continue
                    if gotHeader:
                        temp = re.sub(r'\s+',',',i).split(",")
                        temp[2] = str(str(temp[2])+str(temp[3]))
                        del temp[3]
                        nodeArray.append(temp)
            nodeTable = pd.DataFrame(nodeArray,columns =header)
            for i in range(0, len(nodeTable["Address"])):
                keys.append(nodeTable["Address"].iloc[i])
        except subprocess.CalledProcessError as e:
            result = str(e.output)
            if result.find("Connection refused") >= 0:
                print("Cannot Connect To " + args.db.title() + ", Terminating code")
                sys.exit()
        except:
            print("Something Went Wrong While Getting The Node/s, Terminating code (You can also provide nodes via config)")
            sys.exit()
    else:
        keys = config.get_keys(args.region, args.environ, "key")

    hosts = config.get_keys(args.region, args.environ, args.db)

    if args.debug: print("Total No. of Hosts", len(hosts))
    util.progress(0, len(hosts), args.debug, "Getting Data From Nodes")

    for i, x in enumerate(hosts):
        if args.debug: print("Processing host", (i + 1))
        receive_cfstats(keys, args.region, args.environ, x, args.keySpace, args.table, useSSH, stats)
        sys.stdout.flush()
        util.progress((i + 1), len(hosts), args.debug, "Getting Data From Nodes")
        if args.debug: print("Done processing host", (i + 1))

    print("\nFinished Getting Data")


def receive_cfstats(key, region, environ, x, keySpace, table, useSSH, stats):
    if table != "":
        keySpace += "."

    command = str(
        "nodetool -h " + str(
            x) + " " + stats + " " + keySpace + "" + table + " > data/" + region + "/" + environ + "/" + str(
            x) + ".txt")  # for local cassandra connection

    if useSSH == True:
        command = str("ssh -i ./keys/" + key[
            0] + " " + x + "'nodetool " + stats + " " + keySpace + "" + table + "' > data/" + region + "/" + environ + "/" + x + ".txt")  # for ssh cassandra connection


    status = False

    while status == False:
        status = get_stats(key, command, region, environ, x)


def create_dir(command, region, environ, x):
    if args.debug: print("File / Directory Does Not Exist, Creating New File / Directory!")

    command = str("data/" + region + "/" + environ + "/")

    if not os.path.exists(command):
        if args.debug: print("Creating new Directory :" + command)
        os.makedirs(command)
        return True

    file = str(command + x + ".txt")
    command = str("touch " + file)

    if not os.path.exists(file):
        if args.debug: print("Creating new File :" + file)
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
        return True


def get_stats(key, command, region, environ, x):
    try:
        if args.debug: print("Running the Get_Stats Command")
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
        if args.debug: print("Get_Stats Success")
        return True

    except FileNotFoundError as e:
        create_dir(command, region, environ, x)
        return False

    except subprocess.CalledProcessError as e:
        result = str(e.output)
        if result.find("Directory nonexistent") >= 0:
            create_dir(command, region, environ, x)
            return False
        if result.find("UnknownHostException") >= 0:
            print("Error While Connecting to Server, Skipping This Node")
            os.remove("data/" + region + "/" + environ + "/" + x + ".txt")
            return True
        if result.find("ConnectException") >= 0:
            print("Error While Connecting to Server, Skipping This Node")
            os.remove("data/" + region + "/" + environ + "/" + x + ".txt")
            return True


if __name__ == '__main__':
    main()
