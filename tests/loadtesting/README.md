### Load testing

##### Introduction
we have applied `Load test` to test the performance of our admin endpoints served through [threebot server](https://github.com/threefoldtech/js-sdk), we have used `Locust` to  assess the performance.

#### Technology Used
- `Threebot server` which is Jumpscale is a cloud automation product and a webplatform to develop web application.


- we have used `Locust`.
Locust is an easy-to-use, distributed, user load testing tool. It is intended for load-testing web sites (or other systems) and figuring out how many concurrent users a system can handle. [read more](https://docs.locust.io/en/stable/what-is-locust.html#features)

##### Installation
- Install [js-sdk](https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/quick_start.md) 

- Locust  cannot be installed in poetry environment because we require a different gevent versions, hence, it should be installed outside of js-sdk environment.

it can be installed with pip.
``` bash
$ pip3 install locust
```
If you want the bleeding edge version, you can use pip to install directly from our Git repository. For example, to install the master branch using Python 3
``` bash
$ pip3 install -e git://github.com/locustio/locust.git@master#egg=locust
```
Once Locust is installed, a locust command should be available in your shell. (if you’re not using virtualenv-which you should-make sure your python script directory is on your path)

To see available options, run:
```bash
$ locust --help
```
for more information about the installation [check](https://docs.locust.io/en/stable/installation.html)

#### Run load test
1. Run `3bot`

- open `jsng` shell then
``` python
j.servers.threebot.start_default() 
```
for more information about `3bot` starting [check](https://github.com/threefoldtech/js-sdk/blob/development/docs/wiki/quick_start.md#runnning-3bot)

2. Run `run_locust.sh` bash file

#### Arguments
- `?` for help
- `u` Number of concurrent Locust users (obligatory)
- `r` The rate per second in which users are spawned (obligatory)
- `h` Host to load test (obligatory)
- `p` Path for python script which uses locust in load testing (obligatory)
- `n` Number of port used in the request, default is 8000 (optional)
 

##### Examples
- Help
```bash
bash tests/loadtesting/run_locust.sh -?
```

```bash
Usage: tests/loadtesting/run_locust.sh -u user_number -r hatch_rate -h host -p path
	-u Number of concurrent Locust users
	-r The rate per second in which users are spawned
	-h Host to load test
	-p Path for python script which uses locust in load testing
	-n Number of port used in the request
```
- Execution
``` bash
bash tests/loadtesting/run_locust.sh -u 200 -r 10 -h https://localhost/admin/\#/ -p tests/loadtesting/admin.py -n 8000
```
or
``` bash
bash tests/loadtesting/run_locust.sh -u 200 -r 10 -h https://localhost/admin/\#/ -p tests/loadtesting/admin.py
```