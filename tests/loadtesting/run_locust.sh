#!/bin/bash
helpFunction() {
    echo ""
    echo "Usage: $0 -u user_number -r hatch_rate -h host -p path"
    echo -e "\t-u Number of concurrent Locust users"
    echo -e "\t-r The rate per second in which users are spawned"
    echo -e "\t-h Host to load test"
    echo -e "\t-p Path for python script which uses locust in load testing"
    echo -e "\t-n Number of port used in the request"
    exit 1 # Exit script after printing help
}

while getopts "u:r:h:p:n:" opt; do
    case "$opt" in
    u) user_number="$OPTARG" ;;
    r) hatch_rate="$OPTARG" ;;
    h) host="$OPTARG" ;;
    p) path="$OPTARG" ;;
    n) port_number="$OPTARG" ;;
    ?) helpFunction ;; # Print helpFunction in case parameter is non-existent
    esac
done

# Print helpFunction in case parameters are empty
if [ -z "$user_number" ] || [ -z "$hatch_rate" ] || [ -z "$host" ] || [ -z "$path" ]; then
    echo "Some or all of the parameters are empty"
    helpFunction
fi

# Begin script in case all parameters are correct
echo "$user_number"
echo "$hatch_rate"
echo "$host"
echo "$path"
echo "$port_number"

# If the port number is not specified, we will use the default port 8000
if [ -z "$port_number" ]; then
    export PORTNO="8000"
else
    export PORTNO=$port_number
fi

# Call locust to do the load testing
locust --headless -u $user_number -r $hatch_rate --host $host -f $path
