SDK_PATH="/sandbox/code/github/threefoldtech/js-sdk"

echo "[*] Enabling ssh access ..."
ssh-keygen -A
echo "127.0.0.1       localhost" > /etc/hosts
echo "127.0.0.1       $(hostname)" >> /etc/hosts
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
chmod -R 500 /etc/ssh
service ssh restart
echo $SSHKEY > /root/.ssh/authorized_keys



echo "[*] Switching to the correct version (${SDK_VERSION}) ..."
cd ${SDK_PATH}

poetry_install=false
if ! git diff --quiet `git branch --show-current` origin/$SDK_VERSION -- poetry.lock; then
  # They are differnet
  poetry_install=true
fi

git fetch --all
git reset --hard origin/${SDK_VERSION}

if $poetry_install; then
  poetry install
fi

echo "INSTANCE_NAME=${INSTANCE_NAME}" >> ~/.bashrc
echo "THREEBOT_NAME=${THREEBOT_NAME}" >> ~/.bashrc
echo "BACKUP_PASSWORD=${BACKUP_PASSWORD}" >> ~/.bashrc
echo "BACKUP_TOKEN=${BACKUP_TOKEN}" >> ~/.bashrc
echo "DOMAIN=${DOMAIN}" >> ~/.bashrc

echo "EMAIL_HOST=${EMAIL_HOST}" >> ~/.bashrc
echo "EMAIL_HOST_USER=${EMAIL_HOST_USER}" >> ~/.bashrc
echo "EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}" >> ~/.bashrc
echo "ESCALATION_MAIL=${ESCALATION_MAIL}" >> ~/.bashrc

echo "[*] Starting threebot in background ..."
python3 jumpscale/packages/tfgrid_solutions/scripts/threebot/entrypoint.py
