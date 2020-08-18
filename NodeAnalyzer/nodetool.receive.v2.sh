#!/bin/bash

if [ -z "$1" ]
    then 
        echo $"Usage: $0 {logdirectory} {confdirectory} {data_dest_path} {0|1} (debug)"
        exit 1;
fi

logdirectory=$1
confdirectory=$2

# defaults to data directory, relative to where this script was called from
data_dest_path=${3:-./data}

debug=$4

# whether or not to skip turning data into tarball at the end
skip_archiving=${NODE_ANALYZER_SKIP_ARCHIVING:-false}

# what jmx port to use for nodetool
node_jmx_port=${NODE_ANALYZER_JMX_PORT}

# set custom command to use to run nodetool. Helpful especially for tarball installations, or for testing over ccm
cmd_for_nodetool=${NODE_ANALYZER_NODETOOL_CMD:-nodetool}

# get absolute path to parent dir, so script's paths are more stable
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )


echo $key

receive_nodetool_command() {
    # don't bother sending the -p option if no jmx port specified
    port_option=$([ "${node_jmx_port}" == "" ] && echo "" || echo "-p ${node_jmx_port}")
    node_command="${cmd_for_nodetool} ${1} ${port_option} > $data_dest_path/nodetool/${1}.txt"
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

commands=$(cat $parent_path/nodetool.commands.txt | tr "," "\n")
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

if [ $skip_archiving == false ]; then
  if [ "${debug}" -eq 1 ] ; then echo $(receive_compress) ; fi
  `eval $(receive_compress)`
fi
