#!/bin/bash

after=$1

sleep $after
zinit stop start
# wait until dead
zinit status start | grep Down

start_time=`date +%s`
while [[ $? == 1 ]]; do
    echo "waiting for server to stop"
    current_time=`date +%s`
    if [[ $current_time > $(($start_time + 120)) ]]; then
      zinit kill start SIGKILL
      current_time=$start_time # to not call sigkill twice
    fi
    sleep 1
    zinit status start | grep Down
done
zinit start start
