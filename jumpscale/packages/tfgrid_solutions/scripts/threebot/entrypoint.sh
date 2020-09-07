SDK_PATH="/sandbox/code/github/threefoldtech/js-sdk"

echo "[*] Enabling ssh access ..."
ssh-keygen -A
echo "127.0.0.1       localhost" > /etc/hosts
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
chmod -R 500 /etc/ssh
service ssh restart
echo $SSHKEY > /root/.ssh/authorized_keys

echo "[*] Switching to the correct version (${SDK_VERSION}) ..."
cd ${SDK_PATH}
git fetch --all
git reset --hard origin/${SDK_VERSION}

poetry update
poetry install

echo "INSTANCE_NAME=${INSTANCE_NAME}" >> ~/.bashrc
echo "THREEBOT_NAME=${THREEBOT_NAME}" >> ~/.bashrc
echo "BACKUP_PASSWORD=${BACKUP_PASSWORD}" >> ~/.bashrc
echo "BACKUP_TOKEN=${BACKUP_TOKEN}" >> ~/.bashrc
echo "DOMAIN=${DOMAIN}" >> ~/.bashrc

echo "[*] Starting threebot in background ..."
python3 jumpscale/packages/tfgrid_solutions/scripts/threebot/entrypoint.py
