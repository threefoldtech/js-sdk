#!/bin/bash

after=$1

sleep $after
zinit stop start
# wait until dead

start_time=`date +%s`

while ! zinit status start | grep -q 'pid: 0' ; do
    echo "waiting for server to stop"
    current_time=`date +%s`
    if [[ $current_time > $(($start_time + 120)) ]]; then
      zinit kill start SIGKILL
      current_time=$start_time # to not call sigkill twice
    fi
    sleep 1
done
zinit start start
