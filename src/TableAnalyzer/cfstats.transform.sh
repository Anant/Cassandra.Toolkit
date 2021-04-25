#!/bin/bash

if [ -z "$1" ]
    then 
        echo $"Usage: $0 {region} {environment} {datacenter} {0|1}"
        exit 1;
fi

region=$1
environ=$2
key=$(python ./config.py $1.$2.key)

transform_cfstats() {
        command="python ./cassandra_cfstats2csv.py data/${region}/${environ}/${1}"
        echo $command
}

hosts=$(python ./config.py $1.$2.$3 | tr "," "\n")

#Clean house
#rm -rf data/${region}/${environ}/10*.csv 

for host in $hosts
do
    host_cfstats=$(transform_cfstats ${host})

        echo "Transforming Stats From:" $host_cfstats
        pre_result=$host_cfstats
         #finding "No entry in" result string
        if [ `echo $pre_result | grep -c "No entry" ` -gt 0 ]
          then
            echo "Terminating Code No entry Found !"
            exit 1;
        fi
        if [ "$4" -eq 1 ] ; then echo $pre_result ; fi
        result=`eval $pre_result`
        #chacking for error in result/output
        if [ $? != 0 ]
          then
            echo $result
            echo "Terminating Code Error Occurred!"
            exit 1;
        fi

        echo $result
done

cat data/${region}/${environ}/1*.csv > data/${region}/${environ}/${region}.${environ}.cfstats.csv
python3 ./cassandra_cfstatsCsvAnalyze.py data/${region}/${environ}/${region}.${environ}.cfstats.csv data/${region}/${environ}/${region}.${environ}.cfstats
python3 ./csv2formattedxls.py data/${region}/${environ}/${region}.${environ}.cfstats.pivot.csv data/${region}/${environ}/${region}.${environ}.cfstats.pivot.xlsx

