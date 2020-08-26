#!/bin/bash

# TODO: Add to the docker file
apt-get update;
apt-get install restic;

restic init;

for path in ${BACKUP_PATHS[*]}
do
  restic backup $path;
done

# To restore:
# restic --target TARGET_PATH restore latest
