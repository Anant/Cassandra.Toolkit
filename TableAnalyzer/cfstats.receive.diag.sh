#!/bin/bash

if [ -z "$1" ]
    then 
        echo $"Usage: $0 {region} {environment} {datacenter} {0|1}"
fi

region=$1
environ=$2
key=$(python ./config.py $1.$2.key)
location=$5

receive_cfstats() {
        #command="ssh -i ./keys/$key ${1} \"nodetool cfstats\" > data/${region}/${environ}/${1}.txt"
        command="cat ${location}/nodes/$1/nodetool/cfstats > data/${region}/${environ}/${1}.txt"
	echo $command
}

hosts=$(python ./config.py $1 $2 $3 | tr "," "\n")
    
for host in $hosts
do
    host_cfstats=$(receive_cfstats ${host})

        echo "Retreiving Stats From:" $host_cfstats
        pre_result=$host_cfstats

        if [ "$4" -eq 1 ] ; then echo $pre_result ; fi
        result=`eval $pre_result`
        echo $result
done

