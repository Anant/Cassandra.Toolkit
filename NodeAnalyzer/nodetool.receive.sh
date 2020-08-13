#!/bin/bash

if [ -z "$1" ]
    then 
        echo $"Usage: $0 {logdirectory} {confdirectory} {datacentername} {0|1} (debug) {data_dest_path}"
        exit 1;
fi

logdirectory=$1
confdirectory=$2
datacentername=$3
debug=$4
# defaults to data directory, relative to where this script was called from
data_dest_path=${5:-./data}

echo $key

receive_nodetool_command() {
    node_command="nodetool ${1} > $data_dest_path/nodetool/${1}.txt"
    echo $node_command
}

receive_copy_config_log() {
    copy_command="cp -r ${logdirectory}/* $data_dest_path/log/ && cp -r ${confdirectory}/* $data_dest_path/conf/"
    echo $copy_command
}

receive_compress() {
    compress_command="tar cvfz `hostname -i`.tar.gz $data_dest_path"
    echo $compress_command
}


# make dirs for where our data goes, if doesn't exist yet
mkdir -p $data_dest_path/log
mkdir -p $data_dest_path/conf
mkdir -p $data_dest_path/nodetool/

if [ "${debug}" -eq 1 ] ; then echo $(receive_copy_config_log); fi
`eval $(receive_copy_config_log)`

commands=$(cat nodetool.commands.txt | tr "," "\n")
if [ "${debug}" -eq 1 ] ; then echo $commands ; fi

# Run through each of the commands and save them 
for command in $commands
do
    node_data=$(receive_nodetool_command ${command})

        if [ "${debug}" -eq 1 ] ; then echo echo "Saving Data For:" $node_data ; fi
        pre_result=$node_data
        #finding "No entry in" result string
        if [ `echo $pre_result | grep -c "No entry" ` -gt 0 ]
          then
            echo "Terminating Code No entry Found !"
            exit 1;
        fi

        if [ "${debug}" -eq 1 ] ; then echo $pre_result ; fi
        result=`eval $pre_result`

        #checking for error in result/output
        
        if [ $? != 0 ]
          then
            echo $result
            echo "Terminating Code Error Occurred!"
            exit 1;
        fi
        echo $result
done

if [ "${debug}" -eq 1 ] ; then echo $receive_compress ; fi
`eval $(receive_compress)`
