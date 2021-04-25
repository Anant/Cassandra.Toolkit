import argparse
import config
import os
import subprocess
import sys


parser = argparse.ArgumentParser(
    description='Push The Stats To New Relic Insights',
    usage='{region} {environment} {0|1}')
parser.add_argument('region', type=str, help='Region {us-east-1|usw|us|aws}')
parser.add_argument('environ', type=str, help='Environment {dev|stage|prod}')
parser.add_argument('debug', type=int, help='Debug {0|1}')

args = parser.parse_args()

def main():

    print("Pushing The Stats To NewRelic")

    if not args.debug : print("Getting x_key From Environments")
    x_key = config.get_keys(args.region, args.environ, "x_key")[0]

    if not x_key :
        print("Failed To Get x_key From Environments Terminating The Code")
        sys.exit()

    if not args.debug : print("Getting Relic URL From Environments")

    relic = config.get_keys(args.region, args.environ, "relicDB")[0]

    if not relic:
        print("Failed To Get Relic URL From Environments Terminating The Code")
        sys.exit()

    file = str("data/"+args.region+"/"+args.environ+"/"+args.region+"."+args.environ+".cfstats.pivot.json")

    if not os.path.exists(file):
        print("Stats File not Exists Terminating The Code")
        sys.exit()

    command = str('cat '+file+' | curl -d @- -X POST -H Content-Type: application/json -H X-Insert-Key: '+str(x_key)+' '+str(relic))
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode()

    if output.find("error"):
        print("Failed To Push The Data Terminating The Code")
        print("Error From Command")
        error = (output.split("{")[1]).split("}")[0]
        print(error)
        sys.exit()

    print("Stats Pushed To New Relic Insights")


if __name__ == '__main__':
    main()
