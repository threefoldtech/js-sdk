from jumpscale.loader import j


def renew_cmd(certbot):
    args = [certbot.DEFAULT_NAME]
    args.append("renew")

    for name, value in certbot.to_dict().items():
        if name.endswith("_") or name not in ["work_dir", "config_dir", "logs_dir"]:
            continue

        if value:
            # append only if the field has a value
            name = name.replace("_", "-")
            args.append(f"--{name}")

            # append the value itself only if it's a boolean value
            # boolean options are set by adding name only
            if not isinstance(value, bool):
                args.append(value)

    return args


def check_managed_certificate(certbot):
    cmd = certbot.run_cmd
    cmd.insert(1, "certificates")

    rc, out, err = j.sals.process.execute(cmd)

    if rc > 0:
        j.logger.error(f"Check certificate failed {out}\n{err}")
        return False
    elif out.count("No certificates found") > 0:
        j.logger.error(f"No certificate managed by certbot for {certbot.domain}")
        return False

    return True


threebot_server = j.servers.threebot.get("default")
for p in threebot_server.packages.list_all():
    package = threebot_server.packages.get(p)
    current_nginx_cert = package.nginx_config.nginx.cert  # To revert it again
    package.nginx_config.nginx.cert = False  # To disable generate a certificate
    package.nginx_config.apply()
    renew_command = []
    for w in package.nginx_config.nginx.websites.list_all():
        website = package.nginx_config.nginx.websites.get(w)
        certbot = website.certbot
        if website.domain:
            if check_managed_certificate(certbot):
                # Certificate managed by certbot, Execute renew after check all certificates
                if not renew_cmd:
                    renew_command = renew_cmd(certbot)
                continue
            else:
                # Certifcate not managed by certbot, Run certbot to get a new one
                website.obtain_and_install_certifcate()

    rc, out, err = j.sals.process.exceute(renew_command)
