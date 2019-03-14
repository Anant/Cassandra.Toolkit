#!/bin/bash

if [ -z "$1" ]
    then 
        echo $"Usage: $0 {region} {environment} {datacenter} {0|1}"
        exit 1;
fi

region=$1
environ=$2
key=$(python ./config.py $1.$2.key)

echo $key

receive_cfstats() {
        command="ssh -i ./keys/$key ${1} \"nodetool cfstats\" > data/${region}/${environ}/${1}.txt"
        echo $command
}

hosts=$(python ./config.py $1.$2.$3 | tr "," "\n")

echo $hosts

for host in $hosts
do
    host_cfstats=$(receive_cfstats ${host})

        echo "Retreiving Stats From:" $host_cfstats
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

