vdc_name=$1
user_name=$2
netns_name=$user_name-$vdc_name

ip netns del $netns_name
