import argparse
import subprocess
import os
import sys
import config
import json
import pandas as pd
import re

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
print(args)

def main():
    useSSH = False
    detectTopology = True
    gotHeader = False
    nodeArray = []
    nodeTable = ''
    keys = []
    nodeToolVer=0
    if args.debug: print("Checking " + args.db.title() + " Version")
    command = str("nodetool -h `hostname -i` version")
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
        if args.debug: print("command output")
        if args.debug: print(output.split("\n"))
    except subprocess.CalledProcessError as e:
        result = str(e.output)
        if result.find("Connection refused") >= 0:
            print("Cannot Connect To " + args.db.title() + ", Terminating code")
            sys.exit();
    if args.debug: print(args.db + " Version : " + output)

    if int((output.split(": ")[1])[0]) == 2:
        if args.debug: print("NodeTool Version v2 using nodetool cfstats")
        stats = str("cfstats")
        nodeToolVer = 2
    elif int((output.split(": ")[1])[0]) == 3:
        if args.debug: print("NodeTool Version v3 using nodetool tablestats")
        stats = str("tablestats")
        nodeToolVer = 3
    elif (int((output.split(": ")[1])[0]) == 4) or (int(output.split("\n")[1].split(": ")[1][0]) == 4):
        if args.debug: print("NodeTool Version v4 using nodetool tablestats")
        stats = str("tablestats")
        nodeToolVer = 4

    if (args.keySpace == "") & (args.table != ""):
        print("Please Provide the Key Space Before Table Using -k / --keySapace")
        sys.exit()

    print("Collecting config variables from Config")

    try:
        with open('config/settings.json', 'r') as f:
            setting = json.load(f)
            useSSH = setting['connection']['useSSH']
            detectTopology = setting['connection']['detectTopology']
    except FileNotFoundError:
        print("settings.json File Not Found OR Error While Getting Setting Parameters, Applying Default Settings")

    if detectTopology:
        if args.debug: print("Detechting Nodes")
        command = str("nodetool -h `hostname -i` status")
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
            dataArray = output.split("\n")
            #if args.debug: print(dataArray)
            for i in dataArray:
                if i != '':
                    if i.find("Note:") != -1:
                        continue
                    if i.find("--  Address") != -1:
                        i = re.sub(r'\s+$','',i)
                        header = re.sub(r'\s+',',',i).split(",")
                        #print(re.sub(r'\s+',',',i))
                        #print(header)
                        if nodeToolVer==2:
                            if args.debug: print("Nodetool Version 2")
                            header[4] = str(str(header[4])+str(header[5]))
                            del header[5]
                            header[5] = str(str(header[5])+str(header[6]))
                            del header[6]
                        elif nodeToolVer==3:
                            if args.debug: print("NodeTool Version 3")
                            header[5] = str(str(header[5])+str(header[6]))
                            del header[6]
                        elif nodeToolVer==4:
                            if args.debug: print("Nodetool Version 4")
                            header[4] = str(str(header[4])+str(header[5]))
                            del header[5]
                            header[5] = str(str(header[5])+str(header[6]))
                            del header[6]
                        #print (header)
                        gotHeader = True
                        continue
                    if gotHeader:
                        temp = re.sub(r'\s+',',',i).split(",")
                        #print(temp)
                        temp[2] = str(str(temp[2])+str(temp[3]))
                        del temp[3]
                        #print(temp)
                        nodeArray.append(temp)
            #print ("Total table")
            #print (nodeArray)
            nodeTable = pd.DataFrame(nodeArray,columns =header)
            #print (nodeTable)
            for i in range(0, len(nodeTable["Address"])):
                keys.append(nodeTable["Address"].iloc[i])
        except subprocess.CalledProcessError as e:
            result = str(e.output)
            if result.find("Connection refused") >= 0:
                print("Cannot Connect To " + args.db.title() + ", Terminating code")
                sys.exit();
        except:
            print(sys.exc_info())
            print("Something Went Wrong While Getting The Node/s, Terminating code (You can also provide nodes via config)")
            sys.exit();
    else:
        keys = config.get_keys(args.region, args.environ, "key")

    hosts = config.get_keys(args.region, args.environ, args.db)

    if args.debug: print("Total No. of Hosts", len(hosts))
    progress(0, len(hosts), "Getting Data From Nodes")

    for i, x in enumerate(hosts):
        if args.debug: print("Processing host", (i + 1))
        receive_cfstats(keys, args.region, args.environ, x, args.keySpace, args.table, useSSH, stats)
        sys.stdout.flush()
        progress((i + 1), len(hosts), "Getting Data From Nodes")
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
        if args.debug: print(command)
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
        if args.debug: print("Get_Stats Success")
        return True

    except FileNotFoundError as e:
        create_dir(command, regioni, environ, x)
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


def progress(count, total, suffix=''):
    if not args.debug:
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()


if __name__ == '__main__':
    main()
