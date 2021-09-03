echo "[*] Starting threebot in background ..."

if [ $MINIMAL == "true" ]; then
  [ -f /usr/local/bin/helm ] && chmod u+x /usr/local/bin/helm
  [ -f /sbin/velero ] && chmod u+x /sbin/velero
  python3 jumpscale/packages/tfgrid_solutions/scripts/threebot/minimal_entrypoint.py
else
  echo "INSTANCE_NAME=${INSTANCE_NAME}" >> ~/.bashrc
  echo "THREEBOT_NAME=${THREEBOT_NAME}" >> ~/.bashrc
  echo "BACKUP_PASSWORD=${BACKUP_PASSWORD}" >> ~/.bashrc
  echo "BACKUP_TOKEN=${BACKUP_TOKEN}" >> ~/.bashrc
  echo "DOMAIN=${DOMAIN}" >> ~/.[bashrc
  echo "THREEBOT_WALLET_SECRET=${THREEBOT_WALLET_SECRET}" >> ~/.bashrc

  echo "EMAIL_HOST=${EMAIL_HOST}" >> ~/.bashrc
  echo "EMAIL_HOST_USER=${EMAIL_HOST_USER}" >> ~/.bashrc
  echo "EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}" >> ~/.bashrc
  echo "ESCALATION_MAIL=${ESCALATION_MAIL}" >> ~/.bashrc


  python3 jumpscale/packages/tfgrid_solutions/scripts/threebot/entrypoint.py
fi
