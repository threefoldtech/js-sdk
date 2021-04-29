from shlex import quote

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import get_user_info, login_required

from bottle import Bottle, HTTPResponse, abort, request

app = Bottle()


@app.route("/backup/destroy", method="POST")
@login_required
def destroy():
    """This method will delete username/backups from the backupservers
    --------------------------------------------------------------------------
    * WARNINING: THIS IS A DISTRUCTIVE ACTION. WON'T BE ABLE TO RECOVER FROM *
    --------------------------------------------------------------------------
    """
    ssh_server1 = j.clients.sshclient.get("backup_server1")
    ssh_server2 = j.clients.sshclient.get("backup_server2")
    # validiate user
    data = j.data.serializers.json.loads(request.body.read())
    threebot_name = data.get("threebot_name", "")
    user_info = j.data.serializers.json.loads(get_user_info())
    current_username = threebot_name.split("_")[0]
    logged_in_username = user_info["username"].split(".")[0]

    # check if the user in explorer
    explorer = j.core.identity.me.explorer
    try:
        explorer.users.get(name=threebot_name)
    except j.exceptions.NotFound:
        abort(403, "Forbidden")

    if current_username != logged_in_username:
        abort(401, "Unauthorized")

    status = "Failed to destroy backups, 3Bot name doesn't exist"
    try:
        ssh_server1.sshclient.run(
            "cd ~/backup; htpasswd -D  .htpasswd {threebot_name}; cd /home/backup_config; rm -r {threebot_name}".format(
                threebot_name=quote(threebot_name)
            )
        )
        ssh_server2.sshclient.run(
            "cd ~/backup; htpasswd -D  .htpasswd {threebot_name}; cd /home/backup_config; rm -r {threebot_name}".format(
                threebot_name=quote(threebot_name)
            )
        )
        status = "Destroyed successfully"
    except:
        raise j.exceptions.Value(status)

    return j.data.serializers.json.dumps({"data": {"status": status}})
