from .libraries import *

# Here go all the methods that are not used in the main code

from functools import wraps

def copy_docstring(source_func):
    """Decorator to copy the docstring from another function."""
    def decorator(target_func):
        @wraps(target_func)
        def wrapper(*args, **kwargs):
            return target_func(*args, **kwargs)
        
        # Copy the docstring from source_func to target_func
        wrapper.__doc__ = source_func.__doc__
        
        return wrapper
    
    return decorator

# NOT SURE IF NECESSARY
"""
def _delete_vars(self):
    allowed_vars = self.gridlist1
    method_names = ['_delete_vars', '_rec_format']

    allowed_dict = {var: getattr(self, var) for var in allowed_vars}
    self.__dict__ = allowed_dict

    for method_name in method_names:
        if method_name in self.__class__.__dict__:
            delattr(self.__class__, method_name)
"""