from .libraries import *

def makelist(el: Any) -> list[Any]:
    return el if isinstance(el,list) else [el]

def _check_par(par: set[str], 
               func: str, 
               **kwargs: Any
              ) -> None:
    """
    Checks if a parameter is in the corresponding list
    depending on the function. If the parameter does not
    belong to the list it raises a warning.

    Returns
    -------

        None

    Parameters
    ----------

        - par: list[str]
            the function parameters
        - func: str
            the name of the function
        - **kwargs: dict
            the selected parameters

    """

    # Check if the parameters are in the list
    notfound: list[str] = [(i) for i in kwargs.keys() if i not in par]

    # If the parameters are not in the list, raise a warning
    if len(notfound) > 0:
        warning_message: str = f"""WARNING: elements {str(notfound)} not found! Please check your spelling! (function {func})"""
        warnings.warn(warning_message, UserWarning)

    return None

