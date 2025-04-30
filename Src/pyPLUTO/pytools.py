import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt


def savefig(filename: str | Path = "img.png", bbox: str | None = "tight") -> None:
    raise NotImplementedError(
        "pyPLUTO.savefig is deprecated.\n"
        "Please call savefig from the Image class instead"
    )


def show(block: bool = True) -> None:
    """
    Shows the figures created with the Image class.

    Parameters
    ----------

    - block: bool, default True
        If True, the function blocks until the figure is closed.

    Returns
    -------

    - None

    Notes
    -----

    - None

    ----

    Examples
    ========

    - Example #1: Shows the image created with the Image class

        >>> pp.show()

    """
    plt.show(block=block)

    return None


def ring(length: float = 0.5, freq: int = 440) -> None:
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

    ----

    Examples
    ========

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
    if os.name == "posix":
        # Check if the 'play' command is available on Linux and MacOS
        try:
            os.system(f"play -nq -t alsa synth {length} sine {freq}")
        except UserWarning:
            # If the 'play' command is not available, raise a warning
            text = (
                "pyPLUTO.ring requires the 'play' command from the"
                "'sox' package. \nPlease install it through the command"
                "\n\nsudo apt install sox \n\nand try again."
            )
            warnings.warn(text, UserWarning)
    elif os.name == "nt":
        try:
            # Check if the 'winsound' package is available on Windows
            import winsound

            winsound.Beep(freq, length)
        except UserWarning:
            # If the 'winsound' package is not available, raise a warning
            text = (
                "pyPLUTO.ring requires the 'winsound' package.\n"
                "Please install it through the command"
                "\n\npip install winsound\n\nand try again."
            )
            warnings.warn(text, UserWarning)
    else:
        # If the OS is not Linux, MacOS or Windows, raise a warning
        text = f"pyPLUTO.ring is not implemented for this OS: {os.name}"
        warnings.warn(text, UserWarning)

    # End of the function
    return None
