# Auto ssl with nginx

The aim of this endeavor to find a working replacement to openresty auto ssl.

Currently there a lot of dependecies needed to use openresty auto ssl, including lua rocks which is not the most straight forward thing to build and adds to the overhead.

An alternative will be to use let's ecnrypt with nginx. The `certbot` serves as a client that automates all that is needed to issue a certificate, renew it as well as adjustments to the nginx configuration.

## Certbot

### Installing certbot

It is required to add this repository `ppa:certbot/certbot` and then you can install `certbot` as follows:

```bash
add-apt-repository ppa:certbot/certbot
apt-get install python-certbot-nginx
```

### Using certbot

Getting the certificate is done by simply running this command:

```bash
certbot --nginx -d {domain}
```

The user will be asked to confirm certain agreements and to specify his email to be used for notification.

The command can also be done non interactively as follows:

```bash
certbot --nginx -d {domain} --non-interactive --agree-tos -m email@example.com --nginx-server-root {server root}
```

Certificate should be generated now and will expire in 90 days from date of issue.

#### Auto renewing

`certbot` allows renewing the certificate simply by running the following command:

```bash
certbot renew
```

The command will automatically renew all certificates if they will expire in the next 30 days.

`certbot` handles that by adding a cron job that runs daily to renew the certificate if needed.
