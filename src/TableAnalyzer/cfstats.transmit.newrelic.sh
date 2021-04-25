#!/bin/bash

if [ -z "$1" ]
    then
        echo $"Usage: $0 {region} {environment}"
        exit 1;
fi

key=$(python ./config.py $1.$2.x_key)
if [ $? != 0 ]
  then
    echo $result
    echo "Terminating Code Error Occurred while getting X-key!"
    exit 1;
fi

relic=$(python ./config.py $1.$2.relicDB)
if [ $? != 0 ]
  then
    echo $result
    echo "Terminating Code Error Occurred while getting relic url!"
    exit 1;
fi

cat data/${1}/${2}/${1}.${2}.cfstats.pivot.json | curl -d @- -X POST -H "Content-Type: application/json" -H "X-Insert-Key:" $key $relic
