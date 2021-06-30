"""Certbot Custom Cronjob
This script used as custom certbot cronjob
- Make sure that the certificates for all domains are managed be certbot.
- Renew certificates.

Cronjob Flow:
1. If domain has a no/pre-fetched certificate "Not managed by certbot"  --> Obtain and install a new certificate
2. If domain has a managed certificate "Managed by certbot"             --> continue for other domains
3. Renew all managed certificate if needed (Renewal will only occur if expiration is within 30 days)
"""

from jumpscale.loader import j


def check_managed_certificate(certbot):
    """Check if the certificate managed by certbot or not

    Args:
        certbot (Certbot): certbot object that contains website configurations

    Returns:
        bool: True if managed by certbot, False otherwise
    """
    cmd = certbot.run_cmd
    cmd.insert(1, "certificates")

    rc, out, err = j.sals.process.execute(cmd)

    if rc > 0:
        j.logger.error(f"Check certificate failed {out}\n{err}")
        return False
    elif out.count("No certificates found") > 0:
        j.logger.info(f"No certificate managed by certbot for {certbot.domain}")
        return False

    j.logger.info(f"Certificate managed by certbot for {certbot.domain}")
    return True


def main():
    j.logger.info("Start Certbot Cronjob")
    threebot_server = j.servers.threebot.get("default")
    renew_command = []
    for p in threebot_server.packages.list_all():
        package = threebot_server.packages.get(p)
        package.nginx_config.nginx.cert = False  # To disable generate a certificate
        package.nginx_config.apply(write_config=False)
        j.logger.debug(f"Check Package:{p}")
        for w in package.nginx_config.nginx.websites.list_all():
            website = package.nginx_config.nginx.websites.get(w)
            if website.domain:
                certbot = website.certbot
                if check_managed_certificate(certbot):
                    # Certificate managed by certbot, Execute renew after check all certificates
                    if not renew_command:  # We need to run it one time to get renew command
                        renew_command = certbot.renew_cmd
                    continue
                else:
                    # Certifcate not managed by certbot, Run certbot to get a new one
                    j.logger.info("New certificate will created to be managed by certbot")
                    website.obtain_and_install_certifcate()

    j.logger.info("Excute certbot renew to renew all the managed certificates")
    j.logger.info(f"{' '.join(renew_command)}")
    rc, out, err = j.sals.process.execute(renew_command)

    if rc > 0:
        j.logger.error(f"Renew certificates failed {out}\n{err}")
    else:
        j.logger.info(f"Certificates Renewed\n{out}")


if __name__ == "__main__":
    main()
