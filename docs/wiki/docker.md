# Starting docker container with js-ng installed
## Start usershell with this
```
 poetry run usershell
```
## instantiate docker container from js-ng usershell
```
container.install(name="jsng", image="threefoldtech/js-ng:latest", ports=None, volumes=None, devices=None, identity=None)
# name is the docker container name, default is jsng
# image is the jsng-image you want to run, default is threefoldtech/js-ng:latest
# ports is the port you want to forward
# volumes is the volumes you want to mount on docker
# devices the devices you want to include in docker
# identity is the private key you want to create on docker
# mount_code mount codedir into container,default is True
```
