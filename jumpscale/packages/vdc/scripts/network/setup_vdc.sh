# this will setup a network namespace and start wireguard in it for the specified vdc
# arguments: $1: vdc_name which is the name specified by the user
#            $2: user_name: the 3bot name of the user without (.3bot)
# example: ./setup_vdc.sh testvdc magidentfinal

vdc_name=$1
user_name=$2
netns_name=$user_name-$vdc_name
iface_name=`openssl rand -hex 6`

ip netns add $netns_name
ip link add dev p-$iface_name type veth peer name v-$iface_name
ip link set p-$iface_name up
ip link set v-$iface_name netns $netns_name
ip -n $netns_name link set v-$iface_name up
ip link set dev p-$iface_name master vdc
ip netns exec $netns_name dhclient
ip netns exec $netns_name wg-quick down ~/sandbox/cfg/vdc/wireguard/$user_name/$vdc_name.conf
ip netns exec $netns_name wg-quick up ~/sandbox/cfg/vdc/wireguard/$user_name/$vdc_name.conf
