import sys
import types


def functions_of_module(module_name, filter_fn=lambda x: True):
    """Returns all functions (the function objects) of the given module name.

    The module is looked up in sys.modules.

    Remember that the current module_name can be determined with __name__.
    filter_fn: Like filter(), working on the function name.
    """
    m = sys.modules[module_name]
    return [x for name, x in m.__dict__.iteritems()
               if filter_fn(name) and isinstance(x, types.FunctionType)]
