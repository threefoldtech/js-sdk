SDK_PATH="/sandbox/code/github/threefoldtech/js-sdk"

echo "[*] Enabling ssh access ..."
ssh-keygen -A
echo "127.0.0.1       localhost" > /etc/hosts
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
chmod -R 500 /etc/ssh
service ssh restart
echo $SSHKEY > /root/.ssh/authorized_keys

echo "[*] Disabling threebot connect ..."
jsng 'j.core.config.set("threebot_connect", False)'

echo "[*] Switching to the correct version (${SDK_VERSION}) ..."
cd ${SDK_PATH}
git fetch --all
git reset --hard origin/${SDK_VERSION}

poetry update
poetry install

echo "[*] Starting threebot in background ..."
threebot start --development --domain "${DOMAIN}" --email "${EMAIL}"
