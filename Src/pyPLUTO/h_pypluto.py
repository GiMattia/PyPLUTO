from .libraries import *

def makelist(el: Any) -> list[Any]:
    return el if isinstance(el,list) else [el]

