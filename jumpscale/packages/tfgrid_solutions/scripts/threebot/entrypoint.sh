SDK_PATH="/sandbox/code/github/threefoldtech/js-sdk"

echo "[*] Enabling ssh access ..."
ssh-keygen -A
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
chmod -R 500 /etc/ssh
service ssh restart
echo $SSHKEY > /root/.ssh/authorized_keys

echo "[*] Disabling threebot connect ..."
jsctl config update threebot_connect false

echo "[*] Switching to the correct version (${SDK_VERSION}) ..."
cd ${SDK_PATH}
git fetch --all
git reset --hard origin/${SDK_VERSION}

echo "[*] Starting threebot in background ..."
threebot start --background --development

echo "[*] Sleeping forever ..."
/usr/bin/sleep 1000d
