### Load testing

##### Introduction
we have applied `Load test` to test the performance of our admin endpoints served through [threebot server](https://github.com/threefoldtech/js-sdk), we have used `Locust` to  assess the performance.

#### Technology Used
- [Threebot server](https://github.com/threefoldtech/js-sdk)


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
1. Start `threebot server`
2. Run `run_locust.sh` bash file

#### Arguments
- `?` for help
- `u` Number of concurrent Locust users (obligatory)
- `r` The rate per second in which users are spawned (obligatory)
- `h` Host to load test (obligatory)
- `p` Path for python script which uses locust in load testing (obligatory)
 

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
```
- Execution
``` bash
bash tests/loadtesting/run_locust.sh -u 200 -r 10 -h https://localhost -p tests/loadtesting/admin.py
```
 for Gedis endpoint
 ``` bash
 bash tests/loadtesting/run_locust.sh -u 200 -r 10 -h http://localhost:8000 -p tests/loadtesting/admin_gedis.py
 ```