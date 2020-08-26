#!/bin/bash

# TODO: Add to the docker file
apt-get update;
apt-get install -y restic crontab ;

if restic list snapshots; then
  if [ -z `restic snapshots --json` ]; then
    restic init; 
  else 
      for path in ${BACKUP_PATHS[*]}
      do
        restic --target $path retore latest;
      done 
    fi
else
    restic init;
fi
echo "for path in ${BACKUP_PATHS[*]}; do restic backup $path; done" > /root/backup.sh
echo "0 0 * * *  root bash /root/backup.sh" >> /etc/cron.d/backup