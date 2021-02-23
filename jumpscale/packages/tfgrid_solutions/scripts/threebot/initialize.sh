echo "[*] Starting threebot in background ..."

if [ $MINIMAL == "true" ]; then
  curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl
  mv kubectl /sbin/
  curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
  wget https://github.com/vmware-tanzu/velero/releases/download/v1.5.3/velero-v1.5.3-linux-amd64.tar.gz
  tar -xvf velero-v1.5.3-linux-amd64.tar.gz
  chmod +x velero-v1.5.3-linux-amd64/velero
  mv velero-v1.5.3-linux-amd64/velero /sbin/
  rm -rf velero-v1.5.3-linux-amd64
  apt install etcd-client -y
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
