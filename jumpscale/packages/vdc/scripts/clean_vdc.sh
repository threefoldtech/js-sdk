vdc_name=$1
user_name=$2
netns_name=$user_name-$vdc_name

ifaces=`ip -n $netns_name link | awk -F: '$0 !~ "lo|vir|wl|^[^0-9]"{print $2;getline}'`
iface_name=
for i in $ifaces; do
    prefix=`echo $i |awk '{ printf "%s\n", substr($1,1,2) }'`
    if [ "$prefix" = "v-" ]; then
        v_iface_name=`echo $i |awk '{ printf "%s\n", substr($1,3) }'`
        iface_name=p-${v_iface_name%@*}
    fi
done

ip netns del $netns_name
ip link del $iface_name
