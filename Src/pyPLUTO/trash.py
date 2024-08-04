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