import argparse
import sys
import cassandra_cfstats2csv
import os
import pandas
import subprocess
import config
import cassandra_cfstatsCsvAnalyze

parser = argparse.ArgumentParser(
    description='Collecting config varibales from environments.yaml and Start receiving stats',
    usage='{region} {environment} {datacenter} {c* major version} {0|1}')
parser.add_argument('region', type=str, help='Region {us-east-1|usw|us|aws}')
parser.add_argument('environ', type=str, help='Environment {dev|stage|prod}')
parser.add_argument('db', type=str, help='Datacenter {cassandra|spark}')
parser.add_argument)'version', type=int, help='Cassandra Version: {2|3}')
parser.add_argument('debug', type=int, help='Debug {0|1}')

args = parser.parse_args()


def main():

    print("Generating CSV file From Stats")
    fileNames = []

    #if args.debug: print("Checking " + args.db.title() + " Version")
    #command = str("nodetool version")
    #try:
    #    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()
    #except subprocess.CalledProcessError as e:
    #    result = str(e.output)
    #    if result.find("Connection refused") >= 0:
    #        print("Cannot Connect To " + args.db.title() + ", Terminating code")
    #        sys.exit();
    #if args.debug: print(args.db + " Version : " + output)

    #if int((output.split(": ")[1])[0]) == 2:
    #    if args.debug: print("Cassandra Version v2")
    #    version = 2
    #else:
    #    if args.debug: print("Cassandra Version v3")
    #    version = 3

    version = config.get_keys(args.region, args.environmen, "version")  
    keys = config.get_keys(args.region, args.environ, "key")
    hosts = config.get_keys(args.region, args.environ, args.db)

    if args.debug: print("Total No. of Hosts", len(hosts))
    progress(0, len(hosts), "Generating CSV File form Stats")

    for i, x in enumerate(hosts):
        if args.debug: print("Processing Stats From host", (i+1))
        path = transform_cfstats(keys, args.region, args.environ, x,version)
        if path:
            fileNames.append(path)
        sys.stdout.flush()
        progress((i + 1), len(hosts), "Generating CSV File form Stats")
        if args.debug: print("Done processing Stats", (i+1))

    print("\nFinished, CSV File/s Created")
    print("\nNow Combining CSV Files Form Diffrent Nodes")

    command = str("cat data/" + args.region + "/" + args.environ + "/*.csv > data/" + args.region + "/" + args.environ + "/"+ args.region + "." + args.environ +".cfstats.csv" )
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()

    print("\nMerging Complete.")
    print("\nPivoting The Data.")

    path = "data/" + args.region + "/" + args.environ + "/"+ args.region + "." + args.environ +".cfstats.csv"
    save = "data/" + args.region + "/" + args.environ + "/"+ args.region + "." + args.environ +".cfstats"
    cassandra_cfstatsCsvAnalyze.endStats(path,save)

    print("\nPivoting Complete.")



def transform_cfstats(keys, region, environ, x,version):
    if args.debug: print("Generating CSV File form Stats "+x+".txt")

    path = str("data/" + region + "/" + environ + "/" + x + ".txt")
    save = str("data/" + region + "/" + environ + "/" + x + ".csv")

    if os.path.exists(path):
        result = cassandra_cfstats2csv.generate(path,save,version)
        if result:
            if args.debug: print("Generation of CSV File form Stats "+x+".txt is Compeleted")
            return save
        else:
            print("Fail to Generate CSV")
    else:
        print("\nStats File Not Exists, Skipping This Node")



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
