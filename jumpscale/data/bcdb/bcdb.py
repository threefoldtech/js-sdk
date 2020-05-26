from redis import Redis
import json
from jumpscale.data.bcdb import models as models
from .clients import RedisStorageClient, RedisIndexClient, SonicIndexTextClient, SQLiteIndexSetClient

class BCDB:
    def __init__(self, ns):
        self.ns = ns
        self.storage = RedisStorageClient(ns)
        self.indexer = RedisIndexClient(ns)
        self.indexer_set = SQLiteIndexSetClient(ns)
        self.indexer_text = SonicIndexTextClient(ns)
        self.models = {
            
        }
        self.loaded_models = {

        }
        self.detect_models()
        self.model_model = self.models["model"](self)

    def detect_models(self):
        """It scans all the models and store its classes for later use."""
        for model_name in dir(models):
            model = getattr(models, model_name)
            if isinstance(model, type) and issubclass(model, models.ModelBase):
                self.models[model._name] = model
    
    def save_obj(self, model, obj):
        """Saves the given objects which belongs to model in the db and update the indexes.
        
        Args:
            model (ModelObj): The model object that obj belongs to.
            obj (JSObjBase): The object that will be saved.
        """
        self.indexer_set.set(model, obj)
        self.indexer_text.set(model, obj)
        for prop in model.schema.props.values():
            old_obj = model.get_by('id', obj.id)
            prop_name = prop.name
            index_prop = getattr(obj, prop.name)
            old_index = getattr(old_obj, prop.name) if old_obj else None
            if prop.index:
                self.indexer.set(model, prop_name, index_prop, obj.id, old_index)
        self.storage.set(model, obj.id, obj)

    def model_id_incr(self, model):
        """Increment the id counter in the model and returns the new id.
        Used to assign unique id for each created object.
        
        Args:
            model (ModelObj): The model object.
        
        Returns:
            int: The new unique id
        """
        return self.storage.incr_id(model)

    def get_item_by_id(self, model, id):
        """Gets the object in the model with the given id.
        
        Args:
            model (ModelObj): The model to be searched in.
            id (int): The object's id.
        
        Returns:
            JSObjBase or None: The JSObject with the given id. None if none was found.
        """
        return self.storage.get(model, id)

    def get_entry(self, model, key, val):
        """Search for objects whose key equal val.
        1. It searches in the redis index if key is indexed.
        2. Else, It's searched for in the sqlite index if the key is indexed for range search.
        3. Else, All objects in the db belonging to the given model is scanned linearly to determine the matching object.
        
        Args:
            model (ModelObj): The model in which the key is searched for.
            key (str): The model property that is checked for.
            val (value): The value.
        
        Raises:
            RuntimeError: If the key is not a part of the schema.
        
        Returns:
            JSObjBase or None: The matched object (o: o.key == val). None if none matched.
        """
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if model.schema.props[key].index:
            return self.get_item_from_index(model, key, val)
        elif model.schema.props[key].index_key:
            found = self.get_item_from_index_set(model, key, val, val)
            return found[0] if found else None
        else:
            for obj in self.storage.get_keys_in_model(model):
                if getattr(obj, key) == val:
                    return obj
        return None

    def get_range(self, model, key, min, max):
        """Searches for objects whose key lies between min and max.
        It tries to search for it in the index. If the key is not indexed it loops through all the objects.
        
        Args:
            model (ModelObj): The model in which the key is searched for.
            key (str): The model property that is checked for.
            min (value): The minimum.
            max (value): The maximum.
        
        Raises:
            RuntimeError: If the key is not a part of the schema.
        
        Returns:
            List[JSObjBase]: A list of matched objects (o: o.key >= min and o.key <= max)
        """
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if not model.schema.props[key].index_key:
            return self.get_item_from_index_set(model, key, min, max)
        else:
            result = []
            for obj in self.storage.get_keys_in_model(model):
                    obj_val = getattr(obj, key)
                    if obj_val >= min and obj_val <= max:
                        result.append(obj)
            return result
            

    def get_item_from_index(self, model, key, val):
        """Search for objects whose key equal val. The key must be indexed for search.
        
        Args:
            model (ModelObj): The model in which the key is searched for.
            key (str): The model property that is checked for.
            val (value): The value.
        
        Raises:
            RuntimeError: If the key is not a part of the schema.
            RuntimeError: If the key is not indexed for search.
        
        Returns:
            List[JSObjBase]: A list of matched objects (o: o.key == val)
        """
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if not model.schema.props[key].index:
            raise RuntimeError(f"{key} is not indexed.")
        keyid = self.indexer.get(model, key, val)
        return self.get_item_by_id(model, keyid) if keyid else None

    def get_item_from_index_set(self, model, key, min, max):
        """Searches for objects whose key lies between min and max. The key must be indexed for range search.
        
        Args:
            model (ModelObj): The model in which the key is searched for.
            key (str): The model property that is checked for.
            min (value): The minimum.
            max (value): The maximum.
        
        Raises:
            RuntimeError: If the key is not a part of the schema.
            RuntimeError: If the key is not indexed for range search.
        
        Returns:
            List[JSObjBase]: A list of matched objects (o: o.key >= min and o.key <= max)
        """
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if not model.schema.props[key].index_key:
            raise RuntimeError(f"{key} is not indexed.")
        return [self.get_item_by_id(model, x[0]) for x in self.indexer_set.get(model, key, min, max)]
        

    def get_item_from_index_text(self, model, key, pattern):
        """Searches for objects whose key matches the given pattern inside model. The key must be registered in the text index.
        
        Args:
            model (Modelobj): The model object in which the pattern is searched.
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
        if key not in model.schema.props:
            raise RuntimeError(f"{key} is not a part of {model.name}'s schema")
        if not model.schema.props[key].index_text:
            raise RuntimeError(f"{key} is not indexed for search.")
        return [self.get_item_by_id(model, int(x)) for x in self.indexer_text.get(model, key, pattern)]

    def get_model_by_name(self, model_name):
        """Returns a Model object given its name.
        
        Args:
            model_name (str): The name of the model.
        
        Raises:
            RuntimeError: Raised when no model exists with the given.
        
        Returns:
            ModelObj: The model object.
        """
        if model_name not in self.loaded_models:
            if model_name not in self.models:
                raise RuntimeError("Model not registered")
            self.loaded_models[model_name] = self.models[model_name](self)
        return self.loaded_models[model_name]
