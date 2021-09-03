import inspect
import sys
from functools import wraps
from jumpscale.loader import j


def actor_method(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # verify args and kwargs types
        signature = inspect.signature(func)
        try:
            bound = signature.bind(*args, **kwargs)
        except TypeError as e:
            raise j.exceptions.Value(str(e))

        for name, value in bound.arguments.items():
            annotation = signature.parameters[name].annotation
            if annotation not in (None, inspect._empty) and not isinstance(value, annotation):
                raise j.exceptions.Value(
                    f"parameter ({name}) supposed to be of type ({annotation.__name__}), but found ({type(value).__name__})"
                )

        # call method
        result = func(*bound.args, **bound.kwargs)
        # verify result type
        return_type = signature.return_annotation
        if return_type is inspect._empty or return_type is None:
            return_type = type(None)

        if not isinstance(result, return_type):
            raise j.exceptions.Value(f"method is supposed to return ({return_type}), but it returned ({type(result)})")

        return result

    return wrapper


class BaseActor:
    def __init__(self):
        self.path = None

    @actor_method
    def info(self) -> dict:
        info = {}
        info["path"] = self.path
        info["methods"] = {}

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for name, attr in methods:
            if name.startswith("_"):
                continue

            signature = inspect.signature(attr)
            info["methods"][name] = {}
            info["methods"][name]["args"] = []
            info["methods"][name]["doc"] = attr.__doc__ or ""

            for parameter_name, parameter in signature.parameters.items():
                info["methods"][name]["args"].append((parameter_name, parameter.annotation.__name__))

        return info

    def __validate_actor__(self):
        def validate_annotation(annotation, annotated):
            if annotation is None or annotation is inspect._empty:
                return

            if not (inspect.isclass(annotation) and annotation.__class__ == type):
                raise ValueError("annotation must be a class type")

            if annotation not in (str, int, float, list, tuple, dict, bool):
                if annotation.__module__ == "builtins":
                    raise ValueError(f"unsupported type ({annotation.__name__})")

                for method in ["to_dict", "from_dict"]:
                    if method not in dir(annotation):
                        raise ValueError(
                            f"type ({annotation.__name__}) which annotate {annotated} doesn't have {method} method"
                        )

        result = {"valid": True, "errors": {}}
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for method_name, method_callable in methods:
            if method_name.startswith("_"):
                continue

            result["errors"][method_name] = []
            signature = inspect.signature(method_callable)
            try:
                validate_annotation(signature.return_annotation, "return")
            except ValueError as e:
                result["errors"][method_name].append(str(e))

            for name, parameter in signature.parameters.items():
                try:
                    validate_annotation(parameter.annotation, f"parameter ({name})")
                except ValueError as e:
                    result["errors"][method_name].append(str(e))

        if any(result["errors"].values()):
            result["valid"] = False

        return result
