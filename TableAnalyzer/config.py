import yaml
import argparse


def get_keys(region, environ, key, imp="True"):
    with open("./config/environments.yaml", 'r') as f:
        doc = yaml.load(f)
    data = []
    if region in doc:
        if environ in doc[region]:
            if key in doc[region][environ]:
                item = doc[region][environ][key]
                if type(item) == list:
                    data.append(doc[region][environ][key])
                    if not imp: print(','.join(doc[region][environ][key]))
                else:
                    data = (doc[region][environ][key])
                    if not imp: print(doc[region][environ][key])
            else:
                data = (["No entry"])
                if not imp: print("No entry")
        else:
            data = (["No entry"])
            if not imp: print("No entry")
    else:
        data = (["No entry"])
        if not imp: print("No entry")
    # change no entry to array, because you return as an array, if you pass string, will only pass `N` back to function    
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
