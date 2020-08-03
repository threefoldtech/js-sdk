#!/bin/bash
chown -R postgres:postgres /var/lib/postgresql /etc/postgresql/10 /run/postgresql /var/log/postgresql
chown -R root:ssl-cert /etc/ssl/private
chmod 0640 /etc/ssl/private/ssl-cert-snakeoil.key
service ssh start
service postgresql start
redis-server --daemonize yes
echo "127.0.0.1 localhost" > /etc/hosts
sed -i -z "s/TFHOSTNAME/$1/" /home/user/PeerTube/config/default.yaml
NODE_OPTIONS="--max-old-space-size=4096" npm start
