from .model_model import ModelBase
import os
import importlib

def add_model(file_name):
    m = importlib.import_module("." + file_name[:-3], "jumpscale.data.bcdb.models")
    for attr in dir(m):
        pyattr = getattr(m, attr)
        if isinstance(pyattr, type) and issubclass(pyattr, ModelBase):
            globals()[attr] = pyattr

files = os.listdir(os.path.dirname(__file__))
for f in files:
    if f.endswith("_model.py"):
        add_model(f)