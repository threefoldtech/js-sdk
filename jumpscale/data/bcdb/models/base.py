from jumpscale.god import j
from jumpscale.data.schema import Property
from jumpscale.data.types import Integer, JSObject
import json

class JSObjBase:
    def __init__(self, model):
        self.model = model

    def get_dict(self):
        return self.model.get_dict(self)

    def save(self):
        return self.model.save_obj(self)

    def __str__(self):
        return json.dumps(self.get_dict(), indent=4)

class ModelBase:
    _schema = ""
    _name = ""
    def __init__(self, bcdb):
        self.schema = self._load_schema()
        self.schema.props["id"] = Property()
        self.schema.props["id"].unique = True
        self.schema.props["id"].index = True
        self.schema.props["id"].type = Integer()
        self.schema.props["id"].name = "id"
        
        self.bcdb = bcdb
        self.name = self._name

    def _load_schema(self):
        return j.data.schema.parse_schema(self._schema)
    
    def create_obj(self, data):
        """Create a new object and assign a new id to it with the given data dict.
        Missing props are defaultly initialized.
        
        Args:
            data (dict): The data dict that is used to create the object.
        
        Returns:
            JSObjBase: The newly created 
        """
        o = JSObjBase(self)
        data['id'] = self._incr_id()
        self.set_from_dict(o, data)
        return o

    def _assert_uniqueness(self, obj):
        """Checks that the object doesn't contain an already existing property that is marked as unique.
        
        Args:
            obj (JSObjBase): The JS Object.
        
        Raises:
            RuntimeError: If it contains a duplicate of a unique value.
        """
        for prop in self.schema.props.values():
            if prop.unique:
                dbobj = self.get_by(prop.name, getattr(obj, prop.name))
                if dbobj is not None and dbobj.id != obj.id:
                    raise RuntimeError(f"{prop.name} is unique. One already exists.")
    
    def save_obj(self, obj):
        """Saves the object to the db. It forwards the call to the bcdb client.
        
        Args:
            obj (JSObjBase): The object to be saved.
        """
        self._assert_uniqueness(obj)
        self.bcdb.save_obj(self, obj)

    def _incr_id(self):
        """Increment the id counter and returns the newly incremented unique id.
        
        Returns:
            int: The new id.
        """
        return self.bcdb.model_id_incr(self)
    
    def get_by(self, key, value):
        """Search for objects whose key equal value.
        1. It searches in the redis index if key is indexed.
        2. Else, It's searched for in the sqlite index if the key is indexed for range search.
        3. Else, All objects in the db belonging to the given model is scanned linearly to determine the matching object.
        
        Args:
            key (str): The model property that is checked for.
            val (value): The value.

        Raises:
            RuntimeError: If the key is not a part of the schema.

        Returns:
            JSObjBase or None: The matched object (o: o.key == val). None if none matched.
        """
        return self.bcdb.get_entry(self, key, value)

    def get_range(self, key, min, max):
        return self.bcdb.get_item_from_index_set(self, key, min, max)
    
    def get_pattern(self, key, pattern):
        """Searches for objects whose key matches the given pattern in this model. The key must be registered in the text index.
        
        Args:
            key (str): The model property that the pattern is searched for in.
            pattern (str): The pattern to be searched for.
        
        Notes:
            Currently sonic server matches for some patterns and doesn't for others.

        Raises:
            RuntimeError: If the key is not defined in the model.
            RuntimeError: If the key is not indexed for search
        
        Returns:
            list[JSObjBase]: List of matching objects (o: o.key matches pattern).
        """
        return self.bcdb.get_item_from_index_text(self, key, pattern)
    
    def get_dict(self, obj):
        """Extracts a dict with all attributes from obj.
        
        Args:
            obj (JSObjBase): The object that the data is extracted from.
        
        Returns:
            dict: The data dict.
        """
        d = {}
        for prop in self.schema.props.values():
            prop_name = prop.name
            d[prop_name] = getattr(obj, prop_name)
            if isinstance(prop.type, JSObject):
                d[prop_name] = d[prop_name].get_dict()
        return d

    def set_from_dict(self, o, d):
        """Sets the attributes in the object o to the data from the dict d.
        Default values is used if it's not present in d.
        
        Args:
            o (JSObjBase): The object that will be set.
            d (dict): The dict containing the object new data.
        
        Notes:
            Type checking needs modification.
            It was assumed to receive strings convertable to the defined property.

        Raises:
            ValueError: If a value in the dict doesn't conform to the type checking rules imposed by the model's schema.
        
        Returns:
            JSObjBase: The JSObject after setting its data from the dict d.
        """
        for prop in self.schema.props.values():
            prop_name = prop.name
            if prop_name in d:
                if not prop.type.check(d[prop_name]):
                    raise ValueError("Wrong form")
                if isinstance(prop.type, JSObject):
                    obj_model = self.bcdb.get_model_by_name(prop.defaultvalue)
                    setattr(o, prop_name, obj_model.load_obj_from_dict(d[prop_name]))
                else:
                    setattr(o, prop_name, prop.type.from_str(d[prop_name]))
            else:
                setattr(o, prop_name, prop.type.default)
        return o

    def load_obj_from_dict(self, d):
        """Creates a new object with its data extracted from the d.
        
        Args:
            d (dict): The dict containing the newly created object's attributes.
        
        Returns:
            JSObjBase: The newly created object.
        """
        o = JSObjBase(self)
        self.set_from_dict(o, d)
        return o
