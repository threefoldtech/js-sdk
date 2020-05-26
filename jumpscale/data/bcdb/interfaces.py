
class StorageInterface:
    def get(self, model, obj_id):
        pass

    def set(self, model, obj_id, value):
        pass

    def get_keys_in_model(self, model):
        pass

    def incr_id(self, model):
        pass

class IndexInterface:
    def __init__(self, bcdb_namespace):
        pass

    def get(self, model, index_prop, index_value):
        pass

    def set(self, model, index_prop, index_value, obj_id, old_value=None):
        pass

class IndexSetInterface:
    def __init__(self, bcdb_namespace):
        pass

    def get(self, model, index_prop, min, max):
        pass

    def set(self, model, obj):
        pass

class IndexTextInterface:
    def __init__(self, bcdb_namespace):
        pass

    def set(self, model, obj):
       pass

    def get(self, model, index_prop, pattern):
        pass 

class SerializerInterface:
    def loads(self, model, s):
        pass

    def dumps(self, model, data):
        pass