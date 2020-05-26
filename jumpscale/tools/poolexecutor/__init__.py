from .poolexecutor import PoolExecutor

"""

def sleepf(howlong, name="fun"):
    print("{} is sleeping for {}".format(name, howlong))
    for i in range(howlong):
        print("{} is sleeping slept for {}".format(name, howlong - i))
        gevent.sleep(i)

with j.tools.poolexecutor.PoolExecutor() as p:
    for i in range(5):
        p.task_add(sleepf, i, name="fun{}".format(i))

    gs = p.run()
    print(p.results(gs))


"""