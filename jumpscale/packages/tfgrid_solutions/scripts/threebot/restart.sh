after=$1

sleep $after
zinit stop start
# wait until dead
zinit status start | grep Down
while [[ $? == 1 ]]; do
    echo "waiting for server to stop"
    sleep 1
    zinit status start | grep Down
done
zinit start start
