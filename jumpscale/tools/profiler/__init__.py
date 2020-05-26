"""This module is used to do profiling for methods. profiling can be visulaized or just printed to stdout
How to use it
```
@j.tools.profiler.profiled(visualized=True)
def foo():
  for i in range(10):
    print("test")
```
to do visualizing, add (visualize=True) when u call profiled decorator
example
@j.tools.profiler.profiled() # this will print the profiling results to stdout
j.tools.profiler.profiled(visualized=True) # will launce a server with the visualized profiling on `http://127.0.0.1:8080/snakeviz/%2Fsandbox%2Fcode%2Fgithub%2Fjs-next%2Fjs-ng%2Fresult.prof`
to change port and host
j.tools.profiler.profiled(visualized=True, port="8008", host="0.0.0.0", print_data=True)
this will print data to stdout and launce snakeviz server on this url
`http://127.0.0.1:8080/snakeviz/foo`
"""
from cProfile import Profile
from pstats import Stats
from snakeviz.main import app
import tornado
from subprocess import Popen
import socket


def profiled(visualized=False, host="127.0.0.1", port="8080", print_data=False):
    def do_profiling(func):
        def wrapper(*args, **kwargs):
            profiler = Profile()
            result = profiler.runcall(func, *args, **kwargs)
            if print_data:
                profiler.print_stats()
            filename = func.__name__
            profiler.dump_stats(filename)
            if visualized:
                visualize(filename, host, port)
            return result

        return wrapper

    return do_profiling


def visualize(filename, host="127.0.0.1", port="8080"):
    try:
        Stats(filename)
    except Exception as e:
        print(f"{filename} is not a valid stats file")
        raise e
    try:
        conn = app.listen(port, address=host)
    except socket.error as e:
        print("Port {0} already in use.".format(port))
        raise e

    url = "http://{0}:{1}/snakeviz/{2}".format(host, port, filename)
    print(f"snakeviz web server started on {host}:{port}; enter Ctrl-C to exit")
    print(url)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        conn.stop()
        print("\nBye!")

    return 0
