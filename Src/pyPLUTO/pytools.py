from .libraries import *

def savefig(filename: str | Path = 'img.png', 
            bbox: str | None = 'tight'
           ) -> None:
    warning_message: str = """
    pyPLUTO.savefig is deprecated. 
    Please call savefig from the Image class instead"""
    warnings.warn(warning_message, DeprecationWarning)
    plt.savefig(filename, bbox_inches = bbox)

def show(block: bool = True) -> None:
    plt.show(block = block)

def ring(length: float = 0.5, 
         freq: int = 440
        ) -> None:
    if os.name == 'posix':
        try:
            os.system(f'play -nq -t alsa synth {length} sine {freq}')
        except:
            text = ("pyPLUTO.ring requires the 'play' command from the"
             "'sox' package. \nPlease install it through the command \n"
             "\nsudo apt install sox \n\n"          
             "and try again.")
            raise ImportError(text)
    elif os.name == 'nt':
        try:
            import winsound
            winsound.Beep(freq, length)
        except:
            text = ("pyPLUTO.ring requires the 'winsound' package. \n"
            "Please install it through the command\n\n"

            "pip install winsound\n\n"

            "and try again.")
            raise ImportError(text)
    else:
        text = "pyPLUTO.ring is not implemented for this OS"
        raise NotImplementedError(text)