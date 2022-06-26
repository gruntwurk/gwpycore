import importlib

def class_from_name(class_name):
    """
    Determines the class based on the fully-qualified classname (e.g. src.myapp.member.MemberType)
	"""
    # FIXME Does this work if the src folder is a parent of the app's source root?
    # TODO Needs a unit test
    parts = class_name.rsplit(".", maxsplit=1)
    module_name = parts[0]
    class_name = parts[1]
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class Singleton(type):
    """
    Base class for a singlton. Provides a constructer that ensures only one
    instance the subclass exists at a time. Thus, whenever you need access
    to the singleton, just write the code to construct a new instance and
    let this constructor decide if it actaually needs to be constructed;
    otherwise, it will just return the existing instance.
    """
    # TODO Needs a unit test
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


__all__ = ("Singleton","class_from_name")
