import argparse
import sys
import config
import util
import os

parser = argparse.ArgumentParser(
    description='Collecting config varibales from environments.yaml and Start receiving stats',
    usage=' {region} {environment} {datacenter} {0|1} [-k] [-t]')
parser.add_argument('region', type=str, help='Region {us-east-1|usw|us|aws}')
parser.add_argument('environ', type=str, help='Environment {dev|stage|prod}')
parser.add_argument('db', type=str, help='Database {cassandra|spark}')
parser.add_argument('location', type=str, help= 'Locations {name}')
parser.add_argument('get_all', type=bool, help='if get all data True|False')
parser.add_argument('version', type=int, help='version {2|3}')
parser.add_argument('debug', type=int, help='debugger {0|1}')
args = parser.parse_args()


def main():
    location = args.location
    region = args.region
    if args.get_all:
        file = str(location + '/nodes')
        hosts = os.listdir(file)
    else:
        hosts = config.get_keys(args.region, args.environ, args.db)
    stats = str('cfstats')
    if args.version is 3:
        stats = str('tablestats')
    if len(hosts) > 1:
        for i, host in enumerate(hosts):
            if args.debug: print("Processing files", (i + 1))
            store_path = str('data' + '/' + region + '/' + args.environ + "/" + host + '.txt')
            path = str(location+ '/nodes/' + host + '/nodetool/'+stats)
            fw = open(store_path, 'w')
            for line in open(path):
                fw.write(line.rstrip("\n"))
                fw.write('\n')
            sys.stdout.flush()
            util.progress((i + 1), len(hosts), args.debug, "collecting files")
            if args.debug: print("Done collecting files", (i + 1))
        if args.debug: print("Finish collect all files")
    elif len(hosts) == 1:
        if args.debug: print("Processing file")
        store_path = str('data' + '/' + region + '/' + args.environ + "/" + hosts[0] + '.txt')
        path = str(location + '/nodes/' + hosts[0] + "/nodetool/"+stats)
        fw = open(store_path, 'w')
        for line in open(path):
            fw.write(line.rstrip("\n"))
            fw.write('\n')
        sys.stdout.flush()
        util.progress(1, 1, args.debug, "collecting file")
        if args.debug: print("Finish collect all file")
    else:
        print("no files available")


if __name__ == '__main__':
    main()
