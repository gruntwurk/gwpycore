import importlib


def package_name(module_name: str) -> str:
    """
    Determines the package name of the given module name. The module name is
    the name of the file in which a class or function is defined. The package
    name is the parent folder (just the subfolder name, not the whole path).

    :param module_name: A module name to examine.

    :return: The package name part of the module name.
    """
    module_parts = module_name.split(".")
    pkg_name = ''
    if len(module_parts) >= 2:
        pkg_name = module_parts[-2]
    return pkg_name


def class_from_name(class_name):
    """
    Determines the class based on the class name.

    :param class_name: The fully-qualified class name (e.g. src.myapp.member.MemberType; case sensitive)
    :return: The class type
    """

    # FIXME Does this work if the src folder is a parent of the app's source root?
    # TODO Needs a unit test
    parts = class_name.rsplit(".", maxsplit=1)
    module_name = parts[0]
    class_name = parts[1]
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class Singleton:
    """
    Class decorator that turns the decorated class into a singleton.

    This means that the class' constructer will now only create a new instance
    the first time it's called. Therafter, it will alway return that same (one
    and only) instance.

    Note: type(DecoratedClass()) will no longer be DecoratedClass.
    So, be sure to test that using: isinstance(DecoratedClass(), DecoratedClass)
    """
    def __init__(self, cls):
        self._cls = cls

    def __call__(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)


__all__ = [
    "Singleton",
    "class_from_name",
    "package_name",
]
