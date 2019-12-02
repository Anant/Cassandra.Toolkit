import argparse
import sys
import cassandra_cfstats2csv
import os
import pandas
import subprocess
import config
import cassandra_cfstatsCsvAnalyze
import glob
import util

parser = argparse.ArgumentParser(
    description='Collecting config varibales from environments.yaml and Start receiving stats',
    usage='{region} {environment} {datacenter} {c* major version} {0|1}')
parser.add_argument('region', type=str, help='Region {us-east-1|usw|us|aws}')
parser.add_argument('environ', type=str, help='Environment {dev|stage|prod}')
parser.add_argument('db', type=str, help='Datacenter {cassandra|spark}')
parser.add_argument('version', type=int, help='Cassandra Version: {2|3}')
parser.add_argument('debug', type=int, help='Debug {0|1}')

args = parser.parse_args()


def main():
    print("Generating CSV file From Stats")
    file_names = []
    version = args.version or config.get_keys(args.region, args.environ, "version")
    # question, if version is a mandatory value for input, Do we have to check yml file?
    keys = config.get_keys(args.region, args.environ, "key")
    hosts = config.get_keys(args.region, args.environ, args.db)

    if args.debug: print("Total No. of Hosts", len(hosts))
    util.progress(0, len(hosts), args.debug, "Generating CSV File form Stats")
    for i, x in enumerate(hosts):
        if args.debug: print("Processing Stats From host", (i + 1))
        path = transform_cfstats(keys, args.region, args.environ, x, version)
        if path:
            file_names.append(path)
        sys.stdout.flush()
        util.progress((i + 1), len(hosts), args.debug, "Generating CSV File form Stats")
        if args.debug: print("Done processing Stats", (i + 1))

    print("\nFinished, CSV File/s Created")
    if len(hosts) > 1:
        print("\nNow Combining CSV Files Form Different Nodes")
        os.chdir("data/" + args.region + "/" + args.environ)
        extension = 'csv'
        all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
        combined_csv = pandas.concat([pandas.read_csv(f) for f in all_filenames])
        # export to csv
        combined_csv.to_csv(args.region + "." + args.environ + ".cfstats.csv", index=False, encoding='utf-8-sig')
        print("Finished, CVS files combined")
    else:
        print("One files only, Job done")
    # command = str("cat data/" + args.region + "/" + args.environ + "/*.csv > data/" + args.region + "/" + args.environ + "/"+ args.region + "." + args.environ +".cfstats.csv" )
    # output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()

    # print("\nMerging Complete.")
    # print("\nPivoting The Data.")

    # path = "data/" + args.region + "/" + args.environ + "/"+ args.region + "." + args.environ +".cfstats.csv"
    # save = "data/" + args.region + "/" + args.environ + "/"+ args.region + "." + args.environ +".cfstats"
    # cassandra_cfstatsCsvAnalyze.endStats(path,save)

    # print("\nPivoting Complete.")


def transform_cfstats(keys, region, environ, x, version):
    if args.debug: print("Generating CSV File form Stats " + x + ".txt")

    path = str("data/" + region + "/" + environ + "/" + x + ".txt")
    save = str("data/" + region + "/" + environ + "/" + x + ".csv")
    if args.debug: print(version)
    if os.path.exists(path):
        result = cassandra_cfstats2csv.generate(path, save, version)
        if result:
            if args.debug: print("Generation of CSV File form Stats " + x + ".txt is Compeleted")
            return save
        else:
            print("Fail to Generate CSV")
    else:
        print("\nStats File Not Exists, Skipping This Node")

if __name__ == '__main__':
    main()
