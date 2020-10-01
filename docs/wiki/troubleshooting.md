# For macOS chrome may complain about self-signed certificate. In terminal execute the following

`open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security --ignore-certificate-errors`

# clean up prev installation data
Data is stored in ~/.config/jumpscale/secureconfig/jumpscale. if you want to start over, you can remove that directory using rm ~/.config/jumpscale/secureconfig/jumpscale

There're also some configurations that gets generated e.g (nginx configurations), logs and binaries when copied in ~/sandbox directory

# nginx

## unknown directive auth request 

Happens when `auth_request` module not precompiled

```
auth_request access auth_basic autoindex browser charset empty_gif fastcgi geo grpc gzip limit_conn limit_req map memcached mirror proxy referer rewrite scgi split_clients ssi upstream_hash upstream_ip_hash upstream_keepalive upstream_least_conn upstream_zone userid uwsgi
```


# redis
- misconfigured redis

```
redis.exceptions.ResponseError: MISCONF Redis is configured to save RDB snapshots, but it is currently not able to persist on disk. Commands that may modify the data set are disabled, because this instance is configured to report errors during writes if RDB snapshotting fails (stop-writes-on-bgsave-error option). Please check the Redis logs for details about the RDB error.
```

https://github.com/threefoldtech/js-sdk/issues/1014


