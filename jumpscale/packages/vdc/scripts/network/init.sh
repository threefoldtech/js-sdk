# this will setup the required bridge, NAT and DHCP to be able to connect to vdcs later
# requires an execution argument for the host ip address which will be used for SNAT
# example: ./init.sh 192.168.1.8

apt install dnsmasq -y
sed -i '/nameserver.*/c\nameserver 8.8.8.8' /etc/resolv.conf
systemctl stop systemd-resolved.service
systemctl disable systemd-resolved.service

systemctl stop dnsmasq.service
systemctl disable dnsmasq.service

host_ip=$1

echo "net.ipv4.ip_forward = 1" > /etc/sysctl.conf
echo "net.ipv4.conf.all.proxy_arp = 1" >> /etc/sysctl.conf
sysctl -p /etc/sysctl.conf


# bridge setup
ip link add name vdc type bridge
ip addr add 192.168.200.1/24 dev vdc
ip link set vdc up

iptables -t nat -A POSTROUTING -s 192.168.200.0/24 -j SNAT --to $host_ip

# dhcp config
dnsmasq --dhcp-range=192.168.200.3,192.168.200.254,255.255.255.0 --dhcp-option=3,192.168.200.1 --interface=vdc
