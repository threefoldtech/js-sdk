## Create your backup solution for marketplace

### First after create your two ubuntu server machine , run this script in the two server machines :
```bash
bash /sandbox/code/github/threefoldtech/js-sdk/jumpscale/packages/marketplace/scripts/backup.sh
```
Then add the ```ssh-key``` of the marketplace in two servers.
 
### Second in your marketplace just configure the two servers.
using jsng
```
BACKUP_SERVER1 = "backup_server1"
BACKUP_SERVER2 = "backup_server2"

ssh_server1 = j.clients.sshclient.get(BACKUP_SERVER1)
ssh_server2 = j.clients.sshclient.get(BACKUP_SERVER2)
ssh_server1.host = IP_SERVER1
ssh_server2.host = IP_SERVER2

ssh_server1.save()
ssh_server2.save()
```