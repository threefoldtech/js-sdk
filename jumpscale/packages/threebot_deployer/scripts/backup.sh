#!/bin/bash

cd /root
wget https://github.com/restic/rest-server/releases/download/v0.9.7/rest-server-0.9.7-linux-amd64.gz
gzip -d rest-server-0.9.7-linux-amd64.gz

chmod +x rest-server-0.9.7-linux-amd64
mv /root/rest-server-0.9.7-linux-amd64 /usr/bin/rest-server

apt-get install -y apache2
/etc/init.d/apache2 restart
mkdir /root/backup
touch /root/backup/.htpasswd
rest-server --private-repos --path /root/backup
