from .interfaces import *
from redis import Redis
import json
import sqlite3
from jumpscale.god import j

class JSONSerializer(SerializerInterface):
    def loads(self, model, s):
        return model.load_obj_from_dict(json.loads(s))
        
    def dumps(self, model, data):
        return json.dumps(model.get_dict(data))

class RedisStorageClient(StorageInterface):
    def __init__(self, bcdb_namespace, host="localhost", port=6379, serializer=None):
        self.redis_client = Redis(host=host, port=port)
        self.serializer = serializer or JSONSerializer()
        self.bcdb_namespace = bcdb_namespace

    def get(self, model, obj_id):
        obj_str = self.redis_client.get(f"{self.bcdb_namespace}.{model.name}://{obj_id}")
        return self.serializer.loads(model, obj_str) if obj_str else None
    
    def set(self, model, obj_id, value):
        return self.redis_client.set(f"{self.bcdb_namespace}.{model.name}://{obj_id}", self.serializer.dumps(model, value))
    
    def get_keys_in_model(self, model):
        pattern = f"{self.bcdb_namespace}.{model.name}://*"
        result = []
        cur, keys  = self.redis_client.scan(cursor=0, match=pattern, count=2)
        result.extend(keys)
        while cur != 0:
            cur, keys = self.redis_client.scan(cursor=cur, match=pattern, count=2)
            result.extend(keys)
        return [self.get(model, int(x.split(b'://')[1])) for x in result]
        
    def incr_id(self, model):
        return self.redis_client.incr(f"{self.bcdb_namespace}.{model.name}.lastid")

class RedisIndexClient(IndexInterface):
    def __init__(self, bcdb_namespace, host="localhost", port=6379):
        self.redis_client = Redis(host=host, port=port)
        self.bcdb_namespace = bcdb_namespace

    def get(self, model, index_prop, index_value):
        res = (self.redis_client.get(f"{self.bcdb_namespace}.indexer.{model.name}.{index_prop}://{index_value}"))
        return int(res) if res else None

    def set(self, model, index_prop, index_value, obj_id, old_value=None):
        if old_value:
            self.redis_client.delete(f"{self.bcdb_namespace}.indexer.{model.name}.{index_prop}://{old_value}")
        return self.redis_client.set(f"{self.bcdb_namespace}.indexer.{model.name}.{index_prop}://{index_value}", obj_id)

class SQLiteIndexSetClient(IndexSetInterface):
    def __init__(self, bcdb_namespace):
        self.bcdb_namespace = bcdb_namespace
    
    def _create_if_not_exists(self, model):
        conn = sqlite3.connect(f"{self.bcdb_namespace}_index.db")
        c = conn.cursor()
        table_name = f"{model.name}"
        c.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if c.fetchone()[0] != 0:
            return None
        props = []
        props_str = ""
        for prop in model.schema.props.values():
            if prop.name != 'id' and prop.index_key:
                prop_type = "INTEGER" if isinstance(prop.type, j.data.types.Integer) else "TEXT"
                props_str += f", {prop.name} {prop_type}"
                props.append(prop.name)
        
        c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id int primary key{props_str})")
        for prop in props:
            c.execute(f"CREATE INDEX IF NOT EXISTS {table_name}_{prop}_index on {table_name}({prop})")
        conn.commit()
        conn.close()
        
    def get(self, model, index_prop, min, max):
        self._create_if_not_exists(model)
        conn = sqlite3.connect(f"{self.bcdb_namespace}_index.db")
        c = conn.cursor()
        table_name = f"{model.name}"
        c.execute(f"SELECT id FROM {table_name} WHERE {index_prop} >= ? and {index_prop} <= ?", (min, max))
        res = c.fetchall()
        conn.close()
        return res

    def set(self, model, obj):
        self._create_if_not_exists(model)
        conn = sqlite3.connect(f"{self.bcdb_namespace}_index.db")
        c = conn.cursor()
        table_name = f"{model.name}"
        props_str = "id"
        props = [obj.id]
        for prop in model.schema.props.values():
            if prop.name != "id" and prop.index_key:
                props_str += f", {prop.name}"
                props.append(getattr(obj, prop.name))
            
        c.execute(f"REPLACE INTO {table_name} ({props_str}) VALUES (?{', ?' * (len(props) - 1)})", props)
        conn.commit()
        conn.close()
        

class SonicIndexTextClient(IndexTextInterface):
    def __init__(self, bcdb_namespace):
        self.bcdb_namespace = bcdb_namespace
        try:
            self.sonic_client = j.clients.sonic.new(self.bcdb_namespace)
        except:
            self.sonic_client = j.clients.sonic.get(self.bcdb_namespace)

    def set(self, model, obj):
       for prop in model.schema.props.values():
           if prop.index_text:
               self.sonic_client.push(self.bcdb_namespace, f"{model.name}_{prop.name}", str(obj.id), str(getattr(obj, prop.name)))

    def get(self, model, index_prop, pattern):
        return self.sonic_client.query(self.bcdb_namespace, f"{model.name}_{index_prop}", pattern)
        
               