from .base import ModelBase

class EmployeeModel(ModelBase):
    _schema = """
    @url = employee
    &name** = "" (S)
    age = 0 (I)
    salary** = 0 (I)
    """
    _name = "employee"