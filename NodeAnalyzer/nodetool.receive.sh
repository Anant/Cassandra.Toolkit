#!/bin/bash

if [ -z "$1" ]
    then 
        echo $"Usage: $0 {logdirectory} {confdirectory} {datacentername} {0|1}"
        exit 1;
fi

logdirectory=$1
confdirectory=$2
datacentername=$3

echo $key

receive_nodetool_command() {
        command="nodetool ${1} > nodetool/${1}.txt"
        echo $command
}

commands=$(cat nodetool.commands.txt | tr "," "\n")

echo $commands

for command in $commands
do
    node_data=$(receive_nodetool_command ${command})

        echo "Saving Data For:" $node_data
        pre_result=$node_data
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

