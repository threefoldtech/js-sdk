import gevent


class Job:
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.args = args
        self.kwargs = kwargs


class PoolExecutor:
    def __init__(self):
        self.jobs = []
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass

    def task_add(self, fun, *args, **kwargs):
        self.jobs.append(Job(fun, *args, **kwargs))

    def run(self, die=True):
        try:
            greenlets = [gevent.spawn(job.fun, *job.args, **job.kwargs) for job in self.jobs]
            # print("greenlets: ", greenlets)
            gevent.joinall(greenlets, raise_error=die)
        except Exception as e:
            self.jobs = []
            raise e
        else:
            self.jobs = []
            return greenlets
    
    def results(self, greenlets):
        return [greenlet.value for greenlet in greenlets]


    # def test_simple(self):
    #     with j.tools.poolexecutor.PoolExecutor() as p:
    #         for i in range(5):
    #             p.task_add(sleepf, i, name="fun{}".format(i))

    #         gs = p.run()
    #         p.results(gs)
    
    #     def sleepf(howlong, name="fun"):
    #         print("{} is sleeping for {}".format(name, howlong))
    #         for i in range(howlong):
    #             print("{} is sleeping slept for {}".format(name, howlong - i))
    #             gevent.sleep(i)

    #     for i in range(5):
    #         self.task_add(sleepf, i, name="fun{}".format(i))

    #     self.run()

    # def test_with_errors(self):

    #     def sleepf(howlong, name="fun"):
    #         print("{} is sleeping for {}".format(name, howlong))
    #         for i in range(howlong):
    #             print("{} is sleeping slept for {}".format(name, howlong - i))
    #             gevent.sleep(i)

    #     def sleepf_with_error(howlong, name="fun"):
    #         print("{} is sleeping for {}".format(name, howlong))
    #         for i in range(howlong):
    #             print("{} is sleeping slept for {}".format(name, howlong - i))
    #             gevent.sleep(i)
    #         raise RuntimeError("error here in sleepf_with_error")

    #     for i in range(5):
    #         self.task_add(sleepf, i, name="fun{}".format(i))

    #     self.task_add(sleepf_with_error, i, name="error_fun")

    #     try:
    #         self.run()
    #     except:
    #         print("run has a function that raises and we caught it.")

    # def test_with_results(self):

    #     def sleepf(howlong, name="fun"):
    #         print("{} is sleeping for {}".format(name, howlong))
    #         for i in range(howlong):
    #             print("{} is sleeping slept for {}".format(name, howlong - i))
    #             gevent.sleep(i)
    #         return 7

    #     for i in range(5):
    #         self.task_add(sleepf, i, name="fun{}".format(i))

    #     greenlets = self.run()
    #     results = [greenlet.value for greenlet in greenlets]
    #     assert all(map(lambda x: x == 7, results)) == True
    #     print(results)

    # def test(self):
    #     for f in [self.test_simple, self.test_with_results, self.test_with_errors]:
    #         f()