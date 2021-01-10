# this will setup a network namespace and start wireguard in it for the specified vdc
# arguments: $1: vdc_name which is the name specified by the user
#            $2: user_name: the 3bot name of the user without (.3bot)
# example: ./setup_vdc.sh testvdc magidentfinal

vdc_name=$1
user_name=$2

netns_name=$user_name-$vdc_name

ip netns add $netns_name
ip link add $netns_name-pub type veth peer name $netns_name-pvt
ip link set $netns_name-pub up
ip link set $netns_name-pvt netns $netns_name
ip -n $netns_name link set $netns_name-pvt up
ip link set dev $netns_name-pub master vdc

ip netns exec $netns_name wg-quick up ~/sandbox/cfg/vdc/wireguard/$user_name/$vdc_name.conf
