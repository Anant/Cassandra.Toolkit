import yaml
import sys
import argparse

def get_keys(region, environ, key, imp="True"):

    with open("./config/environments.yaml", 'r') as f:
        doc = yaml.load(f)

    inputArray = [region, environ, key]

    data = []

    if inputArray[0] in doc:
        if inputArray[1] in doc[inputArray[0]]:
            if inputArray[2] in doc[inputArray[0]][inputArray[1]]:
                item = doc[inputArray[0]][inputArray[1]][inputArray[2]]
                if type(item) == list:
                    # this makes data a list with single item, which is a list. 
                    # used if key is e.g., "cassandra" or "spark"
                    data.append(doc[inputArray[0]][inputArray[1]][inputArray[2]])
                    if not imp: print (','.join(doc[inputArray[0]][inputArray[1]][inputArray[2]]))
                else:
                    # used if key is "key", (ie ssh keh). 
                    # data is now a tuple with a single item, so data[0] return just the ssh key
                    data = (doc[inputArray[0]][inputArray[1]][inputArray[2]])
                    if not imp: print (doc[inputArray[0]][inputArray[1]][inputArray[2]])
            else:
                data = ("No entry")
                if not imp: print ("No entry")
        else:
            data = ("No entry")
            if not imp: print ("No entry")
    else:
        data = ("No entry")
        if not imp: print ("No entry")

    return data[0]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Collecting configuration varibales from config/environments.yaml',
        usage='{region} {environment} {key:cassandra|spark|relicDB|x_key}')
    parser.add_argument('region', type=str, help='Region {us-east-1|usw|us|aws}')
    parser.add_argument('environ', type=str, help='Environment {dev|stage|prod}')
    parser.add_argument('key', type=str, help='End Node {key:cassandra|spark|relicDB|x_key}')
    args = parser.parse_args()
    get_keys(args.region, args.environ, args.key, False)
