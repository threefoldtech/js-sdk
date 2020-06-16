- start redis
- `poetry run jsng`
- get `main` instance and make sure to nginx configure` j.sals.nginx.main.configure()`
- start nginx `sudo nginx -c ~/sandbox/cfg/nginx/main/nginx.conf`


```
s = j.servers.threebot.get("aa") 
s.packages.add("/home/xmonader/wspace/threefoldtech/js-ng/jumpscale/packages/foo")  
s.save()
s.start()

```


```
➜  js-ng git:(development_threebot) ✗ curl -XPOST localhost:80/foo/actors/myactor/hello
"hello from foo's actor"%       

```
