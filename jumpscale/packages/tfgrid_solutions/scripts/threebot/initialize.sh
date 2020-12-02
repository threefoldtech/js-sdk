

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
