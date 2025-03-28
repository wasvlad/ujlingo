from test_system.caching import RedisCaching, RedisCachingException, init_redis


class TestRedisCaching:
    class SimpleClass:
        def __init__(self, name):
            self.__name = name

        def get_name(self):
            return self.__name

        def set_name(self, name):
            self.__name = name

    def setup_class(self):
        self.key = "test_key"

    def setup_method(self):
        self.simple_class = self.SimpleClass("simple_class")

    def teardown_method(self):
        r = init_redis()
        res = r.delete(self.key)

    def test_write_ok(self):
        data = self.simple_class
        cache = RedisCaching(self.key, data)
        cache.write()
        assert RedisCaching.load(self.key).get_name() == "simple_class"

    def test_write_fail(self):
        data = self.simple_class
        cache = RedisCaching(self.key, data)
        cache.write()
        cache = RedisCaching(self.key, {"name": "simple_class"})
        try:
            cache.write()
        except RedisCachingException:
            return
        assert False

    def test_update_ok(self):
        data = self.simple_class
        cache = RedisCaching(self.key, data)
        cache.write()
        data.set_name("new_name")
        cache.update()
        assert RedisCaching.load(self.key).get_name() == "new_name"

    def test_update_fail(self):
        data = self.simple_class
        cache = RedisCaching(self.key, data)
        data.set_name("new_name")
        try:
            cache.update()
        except RedisCachingException:
            return
        assert False

    def test_delete_ok(self):
        data = self.simple_class
        cache = RedisCaching(self.key, data)
        cache.write()
        cache.delete()
        try:
            RedisCaching.load(self.key)
        except RedisCachingException:
            return
        assert False

    def test_delete_fail(self):
        cache = RedisCaching(self.key, self.simple_class)
        try:
            cache.delete()
        except RedisCachingException:
            return
        assert False


