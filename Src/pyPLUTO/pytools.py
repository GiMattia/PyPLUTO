from .libraries import *

def savefig(filename: str | Path = 'img.png', 
            bbox: str | None = 'tight'
           ) -> None:
    """
    ...
    """
    warn = "pyPLUTO.savefig is deprecated.\n" \
           "Please call savefig from the Image class instead"
    warnings.warn(warn, DeprecationWarning)
    plt.savefig(filename, bbox_inches = bbox)

def show(block: bool = True) -> None:
    plt.show(block = block)

def ring(length: float = 0.5, 
         freq: int = 440
        ) -> None:
    """
    Makes a sound for a given length and frequency.
    It works on Linux, MacOS and Windows.

    Parameters
    ----------

    - length: float, default 0.5
        The length of the sound in seconds.

    - freq: int, default 440
        The frequency of the sound in Hz.

    Returns
    -------

    - None

    Notes
    -----

    - None

    Examples
    --------

    - Example #1: Make a sound with a frequency of 440 Hz and a length 
      of 0.5 seconds

        >>> ring()

    - Example #2: Make a sound with a frequency of 880 Hz and a length
      of 1 second

        >>> ring(freq = 880)

    - Example #3: Make a sound with a frequency of 220 Hz and a length
      of 0.2 seconds
    
        >>> ring(length = 0.2, freq = 220)
    
    """

    # Check the OS
    if os.name == 'posix':
        # Check if the 'play' command is available on Linux and MacOS
        try:
            os.system(f'play -nq -t alsa synth {length} sine {freq}')
        except:
            # If the 'play' command is not available, raise a warning
            text = "pyPLUTO.ring requires the 'play' command from the" \
                   "'sox' package. \nPlease install it through the command" \
                   "\n\nsudo apt install sox \n\nand try again."         
            warnings.warn(text, UserWarning)
    elif os.name == 'nt':
        try:
            # Check if the 'winsound' package is available on Windows
            import winsound
            winsound.Beep(freq, length)
        except:
            # If the 'winsound' package is not available, raise a warning
            text = "pyPLUTO.ring requires the 'winsound' package.\n" \
                   "Please install it through the command" \
                   "\n\npip install winsound\n\nand try again."
            warnings.warn(text, UserWarning)
    else:
        # If the OS is not Linux, MacOS or Windows, raise a warning
        text = f"pyPLUTO.ring is not implemented for this OS: {os.name}"
        warnings.warn(text, UserWarning)

    # End of the function
    return None
    
