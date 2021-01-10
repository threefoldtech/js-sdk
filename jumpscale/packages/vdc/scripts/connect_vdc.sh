vdc_name=$1
user_name=$2
ip_address=$3

netns_name=$user_name-$vdc_name
ip netns exec $netns_name ssh root@$ip_address -o StrictHostKeyChecking=no
