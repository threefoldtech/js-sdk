import gevent
import time

from unittest import TestCase, skip
from jumpscale.loader import j
from tests.servers.gedis.test_actors.test_actor import TestObject


COUNT = 1000
POOLS_COUNT = 100
DIR_NAME = j.sals.fs.dirname(__file__)
ACTORS_DIR = j.sals.fs.join_paths(DIR_NAME, "test_actors")
TEST_ACTOR_PATH = j.sals.fs.join_paths(ACTORS_DIR, "test_actor.py")
MEMORY_ACTOR_PATH = j.sals.fs.join_paths(ACTORS_DIR, "memory_profiler.py")
RELOADING_ACTOR_PATH = j.sals.fs.join_paths(ACTORS_DIR, "test_reloading.py")
RELOADING_ACTOR_CHANGED_PATH = j.sals.fs.join_paths(ACTORS_DIR, "test_reloading_changed.py")


class TestGedis(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = j.servers.gedis.get("test")
        cls.server.actor_add("test", TEST_ACTOR_PATH)
        cls.server.actor_add("memory", MEMORY_ACTOR_PATH)
        gevent.spawn(cls.server.start)
        assert j.sals.nettools.wait_connection_test(cls.server.host, cls.server.port, 3)
        cls.cl = j.clients.gedis.get("test")

    @classmethod
    def tearDownClass(cls):
        cls.server.actor_delete("test")
        cls.server.actor_delete("memory")
        cls.server.stop()
        j.clients.gedis.delete("test")
        j.servers.gedis.delete("test")

    @skip("https://github.com/threefoldtech/js-ng/issues/421")
    def test_01_basic(self):
        response = self.cl.actors.test.add_two_numbers(5, 15)
        self.assertEqual(response.result, 20)

        response = self.cl.actors.test.concate_two_strings("hello", "world")
        self.assertEqual(response.result, "helloworld")

        obj = TestObject()
        response = self.cl.actors.test.update_object(obj, {"attr_1": 1, "attr_2": 2})
        self.assertEqual(response.result.attr_1, 1)
        self.assertEqual(response.result.attr_2, 2)

        response = self.cl.actors.test.update_objects(
            [obj, obj], [{"attr_1": 1, "attr_2": 2}, {"attr_1": 3, "attr_2": 4}]
        )
        self.assertEqual(response.result[0].attr_1, 1)
        self.assertEqual(response.result[0].attr_2, 2)
        self.assertEqual(response.result[1].attr_1, 3)
        self.assertEqual(response.result[1].attr_2, 4)

    def test02_memory_cleanup(self):
        pool = gevent.pool.Pool(POOLS_COUNT)

        def register(i):
            j.logger.info("Registering actor test_{}", i)
            self.cl.actors.system.register_actor("test_%s" % i, TEST_ACTOR_PATH)

        def execute(i):
            j.logger.info("executing actor no {}", i)
            myobject = TestObject()
            myobject.atrr = i
            response = getattr(self.cl.actors, "test_%s" % i).add_two_numbers(1, 2)
            self.assertEqual(response.result, 3)

        def unregister(i):
            j.logger.info("Unregister actor test_{}", i)
            self.cl.actors.system.unregister_actor("test_%s" % i)

        jobs = []
        for i in range(COUNT):
            jobs.append(pool.spawn(register, i))

        gevent.joinall(jobs)

        self.cl.reload()

        jobs = []
        for i in range(COUNT):
            jobs.append(pool.spawn(execute, i))

        gevent.joinall(jobs)

        jobs = []
        for i in range(COUNT):
            jobs.append(pool.spawn(unregister, i))

        gevent.joinall(jobs)

        self.assertEqual(self.cl.actors.memory.object_count("TestObject").result, 0)

    def test_03_reloading_actors(self):
        """Test actors reloading

        **Test Scenario**

        - Write a simple actor to a file
        - Register and check this actor against a known return value of a known method
        - Register the actor again with and without changes to the known method
        - Check the return value again
        """
        actor = j.sals.fs.read_file(RELOADING_ACTOR_PATH)
        changed_actor = j.sals.fs.read_file(RELOADING_ACTOR_CHANGED_PATH)
        actor_name = "test_reloading_actor"

        with j.sals.fs.TemporaryDirectory() as tmp_dir_path:
            actor_path = j.sals.fs.join_paths(tmp_dir_path, f"{actor_name}.py")

            # register the actor and check get_value()
            # sleep is used here so register requests are handled by the server in the correct order
            j.sals.fs.write_file(actor_path, actor)
            print(self.cl.actors.system.register_actor(actor_name, actor_path))
            self.cl.reload()
            self.assertEqual(self.cl.actors.test_reloading_actor.get_value().result, 1)
            gevent.sleep(1)

            # register changed actor and check get_value() again
            # it should not be changed
            j.sals.fs.write_file(actor_path, changed_actor)
            print(self.cl.actors.system.register_actor(actor_name, actor_path))
            self.assertEqual(self.cl.actors.test_reloading_actor.get_value().result, 1)
            gevent.sleep(1)

            # do previous step, but with force_reload set to True
            print(self.cl.actors.system.register_actor(actor_name, actor_path, force_reload=True))
            # self.cl.reload()
            self.assertEqual(self.cl.actors.test_reloading_actor.get_value().result, 2)
